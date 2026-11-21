# Audience research fetcher

The video workspace can't reach YouTube, Reddit, Google Trends or Wikimedia directly, so this branch does it through GitHub Actions.

1. Edit `request.json` with a new `id`:
```json
{
  "id": "2026-11-22-0241-trending",
  "youtube_queries": ["planet nine", "planet nine shorts"],
  "shorts_only": true,
  "suggest": ["planet nine", "is planet nine"],
  "reddit_queries": ["planet nine"],
  "trends_geo": ["US", "IN", "GB"],
  "wiki_top": true,
  "wiki_articles": ["Planet Nine"],
  "channel_stats": true
}
```
   Limits: 12 YouTube queries, 12 suggest seeds, 8 Reddit queries, 10 Wikipedia articles. Every field is optional.
2. Commit and push this branch. The workflow publishes `results.json` on branch `research` (replaced each time).
3. Poll `git clone --depth 1 --branch research https://github.com/s-shorts/space research` until `results.json` has your `id` (usually 1-3 minutes).

What comes back:
- `youtube[q]`: top results (Shorts filter) with `views`, `age_days`, `views_per_day`, `channel`, `likes`, `comments`; plus `top_views` and `median_views`. Views per day is the best signal of what is hot now.
- `youtube_suggest` / `google_suggest`: what people actually type (autocomplete).
- `reddit[q]`: top posts of the month with score and comment counts.
- `trends[geo]`: Google Trends "trending now" searches with approximate traffic and news headlines.
- `wiki_top`: the most-read English Wikipedia articles yesterday; `wiki_views[a]`: 30 days of daily views with `rising_ratio` (last 3 days vs. before).
- `channel`: our own recent Shorts (target `yt-main`) with views, likes, comments, views per hour since posting, and a `summary` with median, top 5 and bottom 5.
- `errors`: any source that failed (each source is best effort).
