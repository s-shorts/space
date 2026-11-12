# Shorts scheduler

A private, free scheduler that posts queued videos to **YouTube Shorts** and **Instagram Reels** at set times, then deletes the video file.

## Dashboard

**https://s-shorts.github.io/space/** (after GitHub Pages is switched on, see the setup guide). Add videos, choose channels and times, edit or delete scheduled videos, connect channels and see what was posted.

## How it works

1. Videos and their details go into the `queue/` folder on the **`media`** branch. The dashboard does this, and so can Claude or `poster/enqueue.py`.
2. Every 15 minutes GitHub Actions runs `poster/post.py`. Any video whose time has come is posted to each of its channels that is switched on.
3. Once a video is on every switched-on channel it was meant for, its file is deleted, the branch history is squashed so the storage is really freed, and a line is added to `published.jsonl`.

GitHub's timer is not exact: a post can go out 5 to 20 minutes after its slot.

## Channels

`accounts.json` lists any number of YouTube and Instagram channels. Each has a mode (YouTube: `off` / `private` / `public`; Instagram: `off` / `on`) and its own key saved as a repo secret (`YT_<KEY>_REFRESH_TOKEN` or `IG_<KEY>_TOKEN`). Use `public` on YouTube only after the Google audit passes. Manage all of this from the dashboard's Channels tab.

## Posting times

Dashboard → Posting times (stored in `config.json`). Default: 08:00, 11:00, 14:00, 17:00, 20:00 and 22:30 India time.

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
  "targets": ["yt-main", "ig-main"]
}
```

## Testing

Actions → **Post due videos** → Run workflow → tick **Test only**. It shows what would be posted without posting.

`targets` are channel ids from `accounts.json`; leave it out to post to every channel.
