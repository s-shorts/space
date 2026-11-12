#!/usr/bin/env python3
"""Add a finished video to the posting queue.

Run inside a checkout of the `media` branch (or pass --media-dir), then commit and push.

    python3 poster/enqueue.py --media-dir ../media \
        --video black_hole.mp4 --title "What sits inside a black hole?" \
        --description "..." --tags "space,black hole,universe" \
        --caption "Instagram caption with #hashtags"

Without --at, the video takes the next free slot from config.json.
"""
import argparse
import json
import re
import shutil
import sys
from datetime import datetime, timedelta
from pathlib import Path
from zoneinfo import ZoneInfo

ROOT = Path(__file__).resolve().parent.parent
CONFIG = json.loads((ROOT / "config.json").read_text())
ACCOUNTS = json.loads((ROOT / "accounts.json").read_text())["accounts"]
MAX_BYTES = 95 * 1024 * 1024   # GitHub refuses files over 100 MB


def taken_slots(media):
    taken = set()
    for path in (media / "queue").glob("*.json"):
        try:
            taken.add(datetime.fromisoformat(json.loads(path.read_text())["publish_at"]))
        except Exception:
            pass
    log = media / "published.jsonl"
    if log.exists():
        for line in log.read_text().splitlines()[-200:]:
            try:
                taken.add(datetime.fromisoformat(json.loads(line)["publish_at"]))
            except Exception:
                pass
    return taken


def next_slot(media, after=None):
    tz = ZoneInfo(CONFIG["timezone"])
    after = after or datetime.now(tz) + timedelta(minutes=20)
    taken = taken_slots(media)
    day = after.date()
    for _ in range(60):
        for hhmm in CONFIG["daily_slots"]:
            h, m = map(int, hhmm.split(":"))
            slot = datetime(day.year, day.month, day.day, h, m, tzinfo=tz)
            if slot > after and slot not in taken:
                return slot
        day += timedelta(days=1)
    raise SystemExit("No free slot in the next 60 days.")


def slugify(text):
    return re.sub(r"[^a-z0-9]+", "-", text.lower()).strip("-")[:40] or "video"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--media-dir", default=".")
    ap.add_argument("--video", required=True)
    ap.add_argument("--title", required=True)
    ap.add_argument("--description", default="")
    ap.add_argument("--tags", default="", help="comma separated")
    ap.add_argument("--caption", default="", help="Instagram caption; defaults to the description")
    ap.add_argument("--at", help="ISO time with offset, e.g. 2026-11-13T08:00:00+05:30")
    ap.add_argument("--targets", default="",
                    help="comma separated channel ids from accounts.json; default: all channels")
    ap.add_argument("--ai-disclosure", action="store_true",
                    help="tell YouTube the video has realistic AI-made content")
    args = ap.parse_args()

    media = Path(args.media_dir).resolve()
    video = Path(args.video)
    if not video.is_file():
        sys.exit(f"Video not found: {video}")
    if video.stat().st_size > MAX_BYTES:
        sys.exit(f"{video.name} is over 95 MB; re-encode it smaller.")
    if len(args.title) > 100:
        sys.exit("YouTube titles are limited to 100 characters.")
    known = [a["id"] for a in ACCOUNTS]
    platforms = [p.strip() for p in args.targets.split(",") if p.strip()] or known
    if not set(platforms) <= set(known):
        sys.exit(f"Unknown channel. Choose from: {', '.join(known)}")

    if args.at:
        when = datetime.fromisoformat(args.at)
        if when.tzinfo is None:
            sys.exit("--at needs an offset such as +05:30")
    else:
        when = next_slot(media)

    item_id = f"{when:%Y%m%d-%H%M}-{slugify(args.title)}"
    queue = media / "queue"
    queue.mkdir(parents=True, exist_ok=True)
    if (queue / f"{item_id}.json").exists():
        sys.exit(f"{item_id} is already queued.")
    shutil.copyfile(video, queue / f"{item_id}.mp4")
    item = {
        "id": item_id,
        "file": f"{item_id}.mp4",
        "publish_at": when.isoformat(timespec="seconds"),
        "title": args.title,
        "description": args.description,
        "tags": [t.strip() for t in args.tags.split(",") if t.strip()],
        "instagram_caption": args.caption or args.description,
        "targets": platforms,
        "youtube": {"ai_disclosure": bool(args.ai_disclosure)},
        "results": {},
        "attempts": {},
    }
    (queue / f"{item_id}.json").write_text(json.dumps(item, indent=2, ensure_ascii=False) + "\n")
    print(f"queued {item_id} for {when:%a %d %b %H:%M %Z} -> {', '.join(platforms)}")


if __name__ == "__main__":
    main()
