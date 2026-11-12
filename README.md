# Shorts scheduler

A private, free scheduler that posts queued videos to **YouTube Shorts** and **Instagram Reels** at set times, then deletes the video file.

## How it works

1. Videos and their details go into the `queue/` folder on the **`media`** branch (Claude does this, or you can with `poster/enqueue.py`).
2. Every 15 minutes GitHub Actions runs `poster/post.py`. Any video whose time has come is posted to each platform that is switched on.
3. Once a video is on every switched-on platform, its file is deleted, the branch history is squashed so the storage is really freed, and a line is added to `published.jsonl`.

GitHub's timer is not exact: a post can go out 5 to 20 minutes after its slot.

## Switches (repo Settings → Secrets and variables → Actions → Variables)

| Variable | Values | Meaning |
|---|---|---|
| `YOUTUBE_MODE` | `off` / `private` / `public` | `private` is for testing. Use `public` only after the Google audit passes. |
| `INSTAGRAM_MODE` | `off` / `on` | Instagram can be switched on as soon as it is set up. |

Nothing posts until one of these is set.

## Posting times

Edit `config.json`. Default: 08:00, 11:00, 14:00, 17:00, 20:00 and 22:30 India time.

## Setup

- [docs/SETUP.md](docs/SETUP.md): connect YouTube and Instagram (one time).
- [docs/youtube-audit-answers.md](docs/youtube-audit-answers.md): draft answers for Google's YouTube API audit form.

## Queue item format

`queue/<id>.json` next to `queue/<id>.mp4`:

```json
{
  "id": "20261113-0800-black-hole",
  "file": "20261113-0800-black-hole.mp4",
  "publish_at": "2026-11-13T08:00:00+05:30",
  "title": "What sits inside a black hole?",
  "description": "YouTube description",
  "tags": ["space", "black hole"],
  "instagram_caption": "Caption with #hashtags",
  "platforms": ["youtube", "instagram"]
}
```

## Testing

Actions → **Post due videos** → Run workflow → tick **Test only**. It shows what would be posted without posting.
