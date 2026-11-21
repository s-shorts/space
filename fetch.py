"""Download the images listed in request.json into out/ and write out/manifest.json.
Only image files from the allowed hosts are fetched (public-domain / open-licence sources)."""
import json, os, re, urllib.request, urllib.parse
ALLOWED = ("upload.wikimedia.org", "commons.wikimedia.org", "images-assets.nasa.gov", "images.nasa.gov", "photojournal.jpl.nasa.gov",
           "www.nasa.gov", "science.nasa.gov", "esahubble.org", "cdn.esahubble.org", "www.eso.org", "cdn.eso.org", "tile.loc.gov",
           "www.loc.gov", "cdn.loc.gov", "collectionapi.metmuseum.org", "images.metmuseum.org", "ids.si.edu", "openaccess-cdn.clevelandart.org",
           "iiif.wellcomecollection.org", "live.staticflickr.com", "digitalcollections.nypl.org", "images.pexels.com", "cdn.pixabay.com", "images.unsplash.com")
MAX_FILES, MAX_BYTES = 30, 15 * 1024 * 1024
UA = "OwlFilesAssetFetcher/1.0 (https://github.com/s-shorts/space; educational video project)"
req = json.load(open("request.json")); os.makedirs("out", exist_ok=True); res = []
KEY = os.environ.get("POLLINATIONS_API_KEY", "").strip()
CF_ACC = os.environ.get("CF_ACCOUNT_ID", "").strip(); CF_TOK = os.environ.get("CF_API_TOKEN", "").strip()
import time, base64, urllib.error
def cloudflare_image(item):
    """Free tier: 10,000 neurons a day; flux-1-schnell at 4 steps (1024x1024) costs about 58,
    so roughly 170 images a day. No watermark."""
    model = item.get("cf_model", "@cf/black-forest-labs/flux-1-schnell")
    body = dict(prompt=item["prompt"][:2048], steps=min(8, int(item.get("steps", 6))))  # this model takes no seed
    rq = urllib.request.Request(f"https://api.cloudflare.com/client/v4/accounts/{CF_ACC}/ai/run/{model}",
                                data=json.dumps(body).encode(), method="POST",
                                headers={"Authorization": "Bearer " + CF_TOK, "Content-Type": "application/json"})
    try:
        with urllib.request.urlopen(rq, timeout=120) as f:
            out = json.loads(f.read())
    except urllib.error.HTTPError as e:
        body = e.read()[:400].decode("utf-8", "replace")
        raise ValueError(f"cloudflare HTTP {e.code}: {body} (account id length {len(CF_ACC)})")
    img = (out.get("result") or {}).get("image")
    if not img: raise ValueError("cloudflare: " + json.dumps(out.get("errors") or out)[:180])
    return base64.b64decode(img)
def get(url, want, timeout=180):
    with urllib.request.urlopen(urllib.request.Request(url, headers={"User-Agent": UA}), timeout=timeout) as f:
        ct = f.headers.get("Content-Type", "")
        if not ct.startswith(want): raise ValueError("unexpected content type: " + ct)
        return f.read(60 * 1024 * 1024)
# ---- AI-generated images and (with a key) video clips, through Pollinations
gen = []; last = 0.0
for item in req.get("generate", [])[:40]:
    kind = item.get("kind", "image"); name = re.sub(r"[^A-Za-z0-9._-]", "_", item.get("name", ""))[:80]
    r = dict(name=name, kind=kind, prompt=item.get("prompt", ""), ok=False)
    try:
        prompt = urllib.parse.quote(item["prompt"][:900], safe="")
        q = dict(width=int(item.get("width", 1920)), height=int(item.get("height", 1080)), seed=int(item.get("seed", 1)), nologo="true")
        if item.get("model"): q["model"] = item["model"]
        if kind == "video":
            if not KEY: raise ValueError("video needs the POLLINATIONS_API_KEY repository secret")
            if not re.search(r"\.mp4$", name): raise ValueError("video name must end in .mp4")
            q.setdefault("model", "seedance"); q["duration"] = int(item.get("duration", 5)); q["key"] = KEY
            if item.get("image"): q["image"] = item["image"]
            url = "https://gen.pollinations.ai/image/" + prompt + "?" + urllib.parse.urlencode(q); want = "video/"
        else:
            if not re.search(r"\.(jpe?g|png)$", name): raise ValueError("image name must end in .jpg or .png")
            if KEY: q["key"] = KEY; url = "https://gen.pollinations.ai/image/" + prompt + "?" + urllib.parse.urlencode(q)
            else: url = "https://image.pollinations.ai/prompt/" + prompt + "?" + urllib.parse.urlencode(q)
            want = "image/"
        use_cf = kind == "image" and CF_ACC and CF_TOK and item.get("provider", "auto") != "pollinations"
        if use_cf:
            err = None
            for attempt in range(3):
                try:
                    data = cloudflare_image(item); err = None; break
                except Exception as e:
                    err = e; time.sleep(4)
            if err: raise err
            r["provider"] = "cloudflare"
            open(os.path.join("out", name), "wb").write(data); r.update(ok=True, bytes=len(data))
            gen.append(r); print({k: v for k, v in r.items() if k != "prompt"}); continue
        err = None
        for attempt in range(3):
            wait = (3 if KEY else 16) - (time.time() - last)
            if wait > 0: time.sleep(wait)
            try:
                data = get(url, want, 300 if kind == "video" else 120); last = time.time(); err = None; break
            except Exception as e:
                last = time.time(); err = e; time.sleep(10)
        if err: raise err
        open(os.path.join("out", name), "wb").write(data); r.update(ok=True, bytes=len(data))
    except Exception as e:
        r["error"] = re.sub(r"key=[^&\s]+", "key=***", str(e))[:200]
    gen.append(r); print({k: v for k, v in r.items() if k != "prompt"})
models = None
if KEY:
    try: models = json.loads(get("https://gen.pollinations.ai/image/models?key=" + KEY, "application/json", 30))
    except Exception as e: models = "could not list: " + re.sub(r"key=[^&\s]+", "key=***", str(e))[:120]
for item in req.get("files", [])[:MAX_FILES]:
    url = item.get("url", ""); name = re.sub(r"[^A-Za-z0-9._-]", "_", item.get("name", ""))[:80]
    r = dict(name=name, url=url, credit=item.get("credit", ""), licence=item.get("licence", ""), ok=False)
    try:
        host = urllib.parse.urlparse(url).hostname or ""
        if not url.startswith("https://") or host not in ALLOWED: raise ValueError("host not allowed: " + host)
        if not re.search(r"\.(jpe?g|png|webp|gif|tiff?)$", name, re.I): raise ValueError("name must end in an image extension")
        with urllib.request.urlopen(urllib.request.Request(url, headers={"User-Agent": UA}), timeout=60) as f:
            ct = f.headers.get("Content-Type", "")
            if not ct.startswith("image/"): raise ValueError("not an image: " + ct)
            data = f.read(MAX_BYTES + 1)
        if len(data) > MAX_BYTES: raise ValueError("file too large")
        open(os.path.join("out", name), "wb").write(data); r.update(ok=True, bytes=len(data))
    except Exception as e:
        r["error"] = str(e)[:200]
    res.append(r); print(r)
json.dump(dict(id=req.get("id", ""), files=res, generated=gen, has_key=bool(KEY), cloudflare=bool(CF_ACC and CF_TOK), models=models), open("out/manifest.json", "w"), indent=1)
