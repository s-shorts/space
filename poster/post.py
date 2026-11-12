#!/usr/bin/env python3
"""Private video scheduler: posts due videos from the queue to YouTube and Instagram.

Runs from GitHub Actions on a timer. The queue lives on the `media` branch:
    queue/<id>.mp4    the video
    queue/<id>.json   title, caption, publish time, per-platform results
When every enabled platform has the video, both files are deleted and a line
is added to published.jsonl.

Environment:
    MEDIA_DIR        checkout of the media branch (default: media)
    GITHUB_REPOSITORY owner/repo, used to build the public video URL for Instagram
    MEDIA_BRANCH     default: media
    YOUTUBE_MODE     off | private | public   (default off)
    INSTAGRAM_MODE   off | on                 (default off)
    YT_CLIENT_ID, YT_CLIENT_SECRET, YT_REFRESH_TOKEN
    IG_USER_ID, IG_ACCESS_TOKEN, IG_API_VERSION (optional, e.g. v25.0)
    DRY_RUN=1        do everything except call YouTube/Instagram
    GIT_SYNC=1       commit and push the queue state after every result
"""
import json
import os
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
MEDIA_DIR = Path(os.environ.get("MEDIA_DIR", "media")).resolve()
QUEUE = MEDIA_DIR / "queue"
LOG = MEDIA_DIR / "published.jsonl"
REPO = os.environ.get("GITHUB_REPOSITORY", "s-shorts/space")
BRANCH = os.environ.get("MEDIA_BRANCH", "media")
YOUTUBE_MODE = os.environ.get("YOUTUBE_MODE", "off").strip().lower() or "off"
INSTAGRAM_MODE = os.environ.get("INSTAGRAM_MODE", "off").strip().lower() or "off"
DRY_RUN = os.environ.get("DRY_RUN") == "1"
GIT_SYNC = os.environ.get("GIT_SYNC") == "1"
CONFIG = json.loads((ROOT / "config.json").read_text())


class PostError(Exception):
    pass


def now():
    return datetime.now(timezone.utc)


def log(msg):
    print(f"[{now():%H:%M:%S}] {msg}", flush=True)


def enabled_platforms():
    out = []
    if YOUTUBE_MODE in ("private", "public"):
        out.append("youtube")
    if INSTAGRAM_MODE == "on":
        out.append("instagram")
    return out


# ---------------------------------------------------------------- git state
def git(*args, check=True):
    return subprocess.run(["git", "-C", str(MEDIA_DIR), *args], check=check,
                          capture_output=True, text=True)


def sync(message):
    """Commit and push the queue state so a later run never posts twice."""
    if not GIT_SYNC:
        return
    git("add", "-A")
    if git("diff", "--cached", "--quiet", check=False).returncode == 0:
        return
    git("commit", "-m", message)
    for attempt in range(5):
        git("pull", "--rebase", "origin", BRANCH, check=False)
        if git("push", "origin", f"HEAD:{BRANCH}", check=False).returncode == 0:
            return
        time.sleep(3 * (attempt + 1))
    raise SystemExit("Could not push queue state. Stopping so nothing is posted twice.")


# ---------------------------------------------------------------- YouTube
def youtube_token(requests):
    r = requests.post("https://oauth2.googleapis.com/token", timeout=30, data={
        "client_id": os.environ["YT_CLIENT_ID"],
        "client_secret": os.environ["YT_CLIENT_SECRET"],
        "refresh_token": os.environ["YT_REFRESH_TOKEN"],
        "grant_type": "refresh_token",
    })
    if r.status_code != 200:
        raise PostError(f"YouTube sign-in failed ({r.status_code}): {r.text[:300]}")
    return r.json()["access_token"]


def post_youtube(item, video):
    yt = {**CONFIG.get("youtube", {}), **item.get("youtube", {})}
    privacy = "public" if YOUTUBE_MODE == "public" else "private"
    body = {
        "snippet": {
            "title": item["title"][:100],
            "description": item.get("description", ""),
            "tags": item.get("tags", []),
            "categoryId": str(yt.get("category_id", "28")),
        },
        "status": {
            "privacyStatus": privacy,
            "selfDeclaredMadeForKids": bool(yt.get("made_for_kids", False)),
            "containsSyntheticMedia": bool(yt.get("ai_disclosure", False)),
        },
    }
    if DRY_RUN:
        log(f"  DRY RUN youtube ({privacy}): {body['snippet']['title']}")
        return {"id": "dry-run", "url": "https://youtube.com/shorts/dry-run", "privacy": privacy}

    import requests
    token = youtube_token(requests)
    notify = "true" if yt.get("notify_subscribers", True) else "false"
    start = requests.post(
        "https://www.googleapis.com/upload/youtube/v3/videos",
        params={"uploadType": "resumable", "part": "snippet,status", "notifySubscribers": notify},
        headers={"Authorization": f"Bearer {token}",
                 "X-Upload-Content-Type": "video/mp4",
                 "X-Upload-Content-Length": str(video.stat().st_size)},
        json=body, timeout=60)
    if start.status_code != 200:
        raise PostError(f"YouTube refused the upload ({start.status_code}): {start.text[:300]}")
    with open(video, "rb") as fh:
        up = requests.put(start.headers["Location"], data=fh,
                          headers={"Content-Type": "video/mp4"}, timeout=900)
    if up.status_code not in (200, 201):
        raise PostError(f"YouTube upload failed ({up.status_code}): {up.text[:300]}")
    data = up.json()
    got = data.get("status", {}).get("privacyStatus")
    result = {"id": data["id"], "url": f"https://youtube.com/shorts/{data['id']}", "privacy": got}
    if privacy == "public" and got != "public":
        result["warning"] = ("YouTube stored this as private. The Google Cloud project has "
                             "probably not passed the API audit yet.")
        log("  WARNING: " + result["warning"])
    return result


# ---------------------------------------------------------------- Instagram
def ig_base():
    version = os.environ.get("IG_API_VERSION", "").strip()
    return "https://graph.instagram.com" + (f"/{version}" if version else "")


def ig_call(requests, method, path, **params):
    params["access_token"] = os.environ["IG_ACCESS_TOKEN"]
    r = requests.request(method, f"{ig_base()}/{path}", params=params, timeout=60)
    try:
        data = r.json()
    except ValueError:
        data = {"raw": r.text[:300]}
    if r.status_code != 200 or "error" in data:
        raise PostError(f"Instagram error ({r.status_code}): {json.dumps(data)[:400]}")
    return data


def post_instagram(item, video):
    ig = {**CONFIG.get("instagram", {}), **item.get("instagram", {})}
    video_url = f"https://raw.githubusercontent.com/{REPO}/{BRANCH}/queue/{video.name}"
    caption = item.get("instagram_caption") or item.get("description") or item["title"]
    if DRY_RUN:
        log(f"  DRY RUN instagram: {video_url}")
        return {"id": "dry-run", "url": "https://instagram.com/reel/dry-run"}

    import requests
    user = os.environ["IG_USER_ID"]
    container = ig_call(requests, "POST", f"{user}/media",
                        media_type="REELS", video_url=video_url, caption=caption[:2200],
                        share_to_feed="true" if ig.get("share_to_feed", True) else "false")["id"]
    deadline = time.time() + 600
    while True:
        st = ig_call(requests, "GET", container, fields="status_code,status")
        code = st.get("status_code")
        if code == "FINISHED":
            break
        if code in ("ERROR", "EXPIRED"):
            raise PostError(f"Instagram could not process the video: {st.get('status', code)}")
        if time.time() > deadline:
            raise PostError("Instagram took more than 10 minutes to process the video.")
        time.sleep(15)
    media_id = ig_call(requests, "POST", f"{user}/media_publish", creation_id=container)["id"]
    url = None
    try:
        url = ig_call(requests, "GET", media_id, fields="permalink").get("permalink")
    except PostError:
        pass
    return {"id": media_id, "url": url}


POSTERS = {"youtube": post_youtube, "instagram": post_instagram}


# ---------------------------------------------------------------- queue
def load_items():
    items = []
    for path in sorted(QUEUE.glob("*.json")):
        try:
            item = json.loads(path.read_text())
            item["_path"] = path
            item["_due"] = datetime.fromisoformat(item["publish_at"])
            if item["_due"].tzinfo is None:
                raise ValueError("publish_at needs a time zone offset")
            items.append(item)
        except Exception as exc:  # a broken file must not block the others
            log(f"SKIP {path.name}: {exc}")
    return sorted(items, key=lambda i: i["_due"])


def save(item):
    data = {k: v for k, v in item.items() if not k.startswith("_")}
    item["_path"].write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n")


def wanted(item, enabled):
    return [p for p in item.get("platforms", CONFIG["default_platforms"]) if p in enabled]


def pending(item, enabled):
    max_attempts = CONFIG.get("max_attempts", 5)
    out = []
    for p in wanted(item, enabled):
        if item.get("results", {}).get(p, {}).get("status") == "done":
            continue
        if item.get("attempts", {}).get(p, 0) >= max_attempts:
            continue
        out.append(p)
    return out


def finished(item, enabled):
    want = wanted(item, enabled)
    return bool(want) and all(
        item.get("results", {}).get(p, {}).get("status") == "done" for p in want)


def retire(item):
    """Everything is posted: log it and delete the video."""
    entry = {"id": item["id"], "title": item["title"], "publish_at": item["publish_at"],
             "results": item.get("results", {})}
    with open(LOG, "a") as fh:
        fh.write(json.dumps(entry, ensure_ascii=False) + "\n")
    (QUEUE / item["file"]).unlink(missing_ok=True)
    item["_path"].unlink(missing_ok=True)
    log(f"  cleared {item['file']} from storage")


def main():
    enabled = enabled_platforms()
    log(f"platforms on: {enabled or 'none'}  (youtube={YOUTUBE_MODE}, instagram={INSTAGRAM_MODE})"
        + ("  DRY RUN" if DRY_RUN else ""))
    if not enabled:
        log("Nothing is switched on yet. Set YOUTUBE_MODE / INSTAGRAM_MODE in repo variables.")
        return 0
    if not QUEUE.is_dir():
        log("No queue folder yet.")
        return 0

    failures = 0
    posted = 0
    limit = CONFIG.get("max_posts_per_run", 1)
    for item in load_items():
        if finished(item, enabled):          # left over from an interrupted run
            retire(item)
            sync(f"clear {item['id']}")
            continue
        todo = pending(item, enabled)
        if not todo or item["_due"] > now():
            continue
        if posted >= limit:
            log(f"{item['id']} is due too; it goes out on the next run.")
            continue
        video = QUEUE / item["file"]
        if not video.is_file():
            log(f"SKIP {item['id']}: {item['file']} is missing")
            failures += 1
            continue
        log(f"POST {item['id']}  (due {item['publish_at']})")
        posted += 1
        for platform in todo:
            item.setdefault("attempts", {})
            item["attempts"][platform] = item["attempts"].get(platform, 0) + 1
            try:
                result = POSTERS[platform](item, video)
                result.update(status="done", at=now().isoformat(timespec="seconds"))
                log(f"  {platform}: {result.get('url')}")
            except Exception as exc:
                failures += 1
                result = {"status": "failed", "error": str(exc)[:500],
                          "at": now().isoformat(timespec="seconds")}
                log(f"  {platform} FAILED (attempt {item['attempts'][platform]}): {exc}")
            item.setdefault("results", {})[platform] = result
            save(item)
            sync(f"{item['id']}: {platform} {result['status']}")
        if finished(item, enabled):
            retire(item)
            sync(f"clear {item['id']}")
    log(f"done: {posted} posted, {failures} problem(s)")
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
