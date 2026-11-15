"""Real photos from Wikimedia Commons (searched, open licences only) + AI images from Pollinations."""
import json, os, re, time, urllib.request, urllib.parse, html
UA = "SleepDocAssetFetcher/1.0 (https://github.com/s-shorts/space; educational documentary)"
R = json.load(open("assets_request.json")); os.makedirs("out/photos", exist_ok=True); os.makedirs("out/ai", exist_ok=True)
FREE = re.compile(r"public domain|pd|cc0|cc[- ]by", re.I)

def get(url, timeout=120, tries=4):
    for a in range(tries):
        try:
            with urllib.request.urlopen(urllib.request.Request(url, headers={"User-Agent": UA}), timeout=timeout) as f:
                return f.read(), f.headers.get("Content-Type", "")
        except urllib.error.HTTPError as e:
            if e.code == 429: time.sleep(20 * (a + 1)); continue
            raise
        except Exception:
            if a == tries - 1: raise
            time.sleep(8)
    raise RuntimeError("too many retries")

photos = []
for q in R["photos"]:
    api = "https://commons.wikimedia.org/w/api.php?" + urllib.parse.urlencode(dict(
        action="query", format="json", generator="search", gsrnamespace=6, gsrsearch=q["q"], gsrlimit=8,
        prop="imageinfo", iiprop="url|extmetadata|size|mime", iiurlwidth=2000))
    try:
        data = json.loads(get(api)[0]); pages = sorted(data.get("query", {}).get("pages", {}).values(), key=lambda p: p.get("index", 99))
    except Exception as e:
        print("search fail", q, e); continue
    n = 0
    for p in pages:
        ii = (p.get("imageinfo") or [{}])[0]; md = ii.get("extmetadata", {})
        if ii.get("mime") not in ("image/jpeg", "image/png", "image/tiff"): continue
        lic = md.get("LicenseShortName", {}).get("value", "")
        if not FREE.search(lic): continue
        if ii.get("width", 0) < 900: continue
        url = ii.get("thumburl") or ii.get("url"); name = f"{q['id']}_{n}.jpg" if ii.get("mime") != "image/png" else f"{q['id']}_{n}.png"
        try:
            b, ct = get(url); open(f"out/photos/{name}", "wb").write(b)
        except Exception as e:
            print("dl fail", url, e); continue
        artist = re.sub("<[^>]+>", "", html.unescape(md.get("Artist", {}).get("value", "")))[:120]
        photos.append(dict(name=name, query=q["q"], title=p["title"], licence=lic, credit=artist, page=ii.get("descriptionurl")))
        print("ok", name, p["title"], lic, flush=True); n += 1; time.sleep(2)
        if n >= q.get("n", 2): break
json.dump(photos, open("out/photos/manifest.json", "w"), indent=1)

KEY = os.environ.get("POLLINATIONS_API_KEY", "").strip(); gen = []; last = 0
for g in R["ai"]:
    q = dict(width=g.get("w", 1920), height=g.get("h", 1080), seed=g.get("seed", 3), nologo="true", model=g.get("model", "flux"))
    pr = urllib.parse.quote(g["prompt"][:900], safe="")
    url = ("https://gen.pollinations.ai/image/" + pr + "?" + urllib.parse.urlencode({**q, "key": KEY})) if KEY else \
          ("https://image.pollinations.ai/prompt/" + pr + "?" + urllib.parse.urlencode(q))
    ok = False
    for a in range(3):
        w = (3 if KEY else 16) - (time.time() - last)
        if w > 0: time.sleep(w)
        try:
            b, ct = get(url, 180, 1); last = time.time()
            if ct.startswith("image/"): open(f"out/ai/{g['name']}", "wb").write(b); ok = True; break
            print("bad ct", ct)
        except Exception as e:
            last = time.time(); print("ai retry", g["name"], str(e)[:120]); time.sleep(10)
    gen.append(dict(name=g["name"], ok=ok, prompt=g["prompt"])); print("ai", g["name"], ok, flush=True)
json.dump(dict(generated=gen, has_key=bool(KEY)), open("out/ai/manifest.json", "w"), indent=1)
