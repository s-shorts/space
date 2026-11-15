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
json.dump(dict(id=req.get("id", ""), files=res), open("out/manifest.json", "w"), indent=1)
