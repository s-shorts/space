#!/usr/bin/env python3
"""Audience research fetcher, run by GitHub Actions (the video workspace can't reach these sites).

Reads request.json and writes out/results.json:
  youtube        : for each query, the top Shorts/videos with views, age, channel and views-per-day
  youtube_suggest: what people type into YouTube search (autocomplete) for each seed
  google_suggest : the same for Google search
  reddit         : top posts of the past month (score, comments) for each query
  trends         : Google Trends "trending now" searches with approximate traffic (geo list)
  wiki_top       : the most-read English Wikipedia articles yesterday (what the world is reading)
  wiki_views     : 30-day daily views of given Wikipedia articles, with a recent-vs-before ratio
  channel        : views and likes of our own recent YouTube Shorts (from published.jsonl on media),
                   with views per hour since posting, for learning what works on the channel
Every part is best effort: a failing source records its error and the rest still runs.
"""
import datetime as dt
import json
import re
import sys
import time
import traceback
import urllib.parse
from pathlib import Path

import requests

UA = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/124.0 Safari/537.36")
S = requests.Session()
S.headers.update({"User-Agent": UA, "Accept-Language": "en-US,en;q=0.9"})
S.cookies.set("CONSENT", "YES+cb", domain=".youtube.com")
S.cookies.set("SOCS", "CAI", domain=".youtube.com")
NOW = dt.datetime.now(dt.timezone.utc)
OUT = Path("out")


def num(text):
    """'1.2M views' -> 1200000; '12,345 views' -> 12345; 'No views' -> 0."""
    if not text:
        return None
    t = text.replace(",", "").strip()
    m = re.search(r"([\d.]+)\s*([KMB]?)", t, re.I)
    if not m:
        return 0 if "no view" in t.lower() else None
    v = float(m.group(1)) * {"": 1, "K": 1e3, "M": 1e6, "B": 1e9}[m.group(2).upper()]
    return int(v)


def age_days(text):
    """'3 days ago' -> 3; 'Streamed 2 weeks ago' -> 14."""
    if not text:
        return None
    m = re.search(r"(\d+)\s*(second|minute|hour|day|week|month|year)", text)
    if not m:
        return None
    n = int(m.group(1))
    return n * {"second": 1 / 86400, "minute": 1 / 1440, "hour": 1 / 24, "day": 1, "week": 7,
                "month": 30, "year": 365}[m.group(2)]


def yt_initial_data(html):
    m = re.search(r"var ytInitialData\s*=\s*(\{.*?\});\s*</script>", html, re.S) or \
        re.search(r"window\[\"ytInitialData\"\]\s*=\s*(\{.*?\});", html, re.S)
    return json.loads(m.group(1)) if m else {}


def walk(o):
    if isinstance(o, dict):
        yield o
        for v in o.values():
            yield from walk(v)
    elif isinstance(o, list):
        for v in o:
            yield from walk(v)


def text_of(x):
    if not x:
        return ""
    if isinstance(x, str):
        return x
    if "simpleText" in x:
        return x["simpleText"]
    if "runs" in x:
        return "".join(r.get("text", "") for r in x["runs"])
    if "content" in x:
        return x["content"]
    return ""


def youtube_search(q, shorts=True, limit=20):
    sp = "&sp=EgIYAQ%253D%253D" if shorts else ""   # "under 4 minutes"
    r = S.get(f"https://www.youtube.com/results?search_query={urllib.parse.quote(q)}{sp}", timeout=30)
    r.raise_for_status()
    data = yt_initial_data(r.text)
    seen, items = set(), []
    for d in walk(data):
        if "videoRenderer" in d:
            v = d["videoRenderer"]
            vid = v.get("videoId")
            item = {"id": vid, "title": text_of(v.get("title")),
                    "views": num(text_of(v.get("viewCountText"))),
                    "age": text_of(v.get("publishedTimeText")),
                    "channel": text_of(v.get("ownerText")),
                    "length": text_of(v.get("lengthText")), "type": "video"}
        elif "shortsLockupViewModel" in d:
            v = d["shortsLockupViewModel"]
            vid = (v.get("onTap", {}).get("innertubeCommand", {}).get("reelWatchEndpoint", {})
                   .get("videoId")) or str(v.get("entityId", "")).replace("shorts-shelf-item-", "")
            meta = v.get("overlayMetadata", {})
            item = {"id": vid, "title": text_of(meta.get("primaryText")),
                    "views": num(text_of(meta.get("secondaryText"))),
                    "age": "", "channel": "", "length": "", "type": "short"}
        elif "reelItemRenderer" in d:
            v = d["reelItemRenderer"]
            vid = v.get("videoId")
            item = {"id": vid, "title": text_of(v.get("headline")),
                    "views": num(text_of(v.get("viewCountText"))),
                    "age": "", "channel": "", "length": "", "type": "short"}
        else:
            continue
        if not vid or vid in seen:
            continue
        seen.add(vid)
        days = age_days(item["age"])
        item["age_days"] = days
        item["views_per_day"] = int(item["views"] / max(days, 0.5)) if item["views"] and days else None
        items.append(item)
        if len(items) >= limit:
            break
    return items


def video_details(vid):
    """Fill in age and channel for Shorts found on the shelf (the shelf hides them)."""
    r = S.get(f"https://www.youtube.com/watch?v={vid}", timeout=30)
    h = r.text
    out = {}
    m = re.search(r'"viewCount":"(\d+)"', h)
    out["views"] = int(m.group(1)) if m else None
    m = re.search(r'"(?:uploadDate|publishDate)":"([^"]+)"', h)
    out["published"] = m.group(1) if m else None
    m = re.search(r'"ownerChannelName":"([^"]*)"', h)
    out["channel"] = m.group(1) if m else ""
    m = re.search(r'"likeCount":"?(\d+)', h) or \
        re.search(r'along with ([\d,]+) other (?:people|person)', h)
    out["likes"] = int(m.group(1).replace(",", "")) if m else None
    m = re.search(r'"title":"((?:[^"\\]|\\.)*)","lengthSeconds"', h)
    if m:
        out["title"] = json.loads(f'"{m.group(1)}"')
    m = re.search(r'"commentCount":"?(\d+)', h)
    out["comments"] = int(m.group(1)) if m else None
    return out


def published_days(p):
    try:
        t = dt.datetime.fromisoformat(p.replace("Z", "+00:00"))
        if t.tzinfo is None:
            t = t.replace(tzinfo=dt.timezone.utc)
        return max((NOW - t).total_seconds() / 86400, 1 / 24)
    except Exception:
        return None


def suggest(q, yt=True):
    url = "https://suggestqueries.google.com/complete/search?client=firefox&hl=en"
    url += ("&ds=yt" if yt else "") + "&q=" + urllib.parse.quote(q)
    r = S.get(url, timeout=20)
    r.raise_for_status()
    return r.json()[1]


def reddit(q, limit=12):
    for host in ("https://www.reddit.com", "https://old.reddit.com"):
        r = S.get(f"{host}/search.json", params={"q": q, "sort": "top", "t": "month", "limit": limit},
                  headers={"User-Agent": "shorts-research/1.0 (by s-shorts)"}, timeout=20)
        if r.ok:
            return [{"title": c["data"]["title"], "subreddit": c["data"]["subreddit"],
                     "score": c["data"]["score"], "comments": c["data"]["num_comments"],
                     "url": "https://www.reddit.com" + c["data"]["permalink"]}
                    for c in r.json()["data"]["children"]]
    raise RuntimeError(f"reddit HTTP {r.status_code}")


def trends(geo):
    r = S.get(f"https://trends.google.com/trending/rss?geo={geo}", timeout=20)
    r.raise_for_status()
    out = []
    for item in re.findall(r"<item>(.*?)</item>", r.text, re.S):
        title = re.search(r"<title>(.*?)</title>", item, re.S)
        traffic = re.search(r"<ht:approx_traffic>(.*?)</ht:approx_traffic>", item)
        news = re.findall(r"<ht:news_item_title>(.*?)</ht:news_item_title>", item)
        out.append({"query": title.group(1) if title else "", "traffic": traffic.group(1) if traffic else "",
                    "news": [re.sub(r"<[^>]+>|&#39;|&quot;", "", n) for n in news[:2]]})
    return out


def wiki_top(limit=60):
    day = NOW - dt.timedelta(days=1)
    url = ("https://wikimedia.org/api/rest_v1/metrics/pageviews/top/en.wikipedia/all-access/"
           f"{day:%Y/%m/%d}")
    r = S.get(url, headers={"User-Agent": "shorts-research/1.0 (github.com/s-shorts/space)"}, timeout=20)
    r.raise_for_status()
    arts = r.json()["items"][0]["articles"]
    skip = ("Main_Page", "Special:", "Wikipedia:", "Portal:", "File:", "Help:", "-")
    return [{"article": a["article"], "views": a["views"]} for a in arts
            if not a["article"].startswith(skip)][:limit]


def wiki_views(article):
    end = NOW - dt.timedelta(days=1)
    start = end - dt.timedelta(days=30)
    url = ("https://wikimedia.org/api/rest_v1/metrics/pageviews/per-article/en.wikipedia/all-access/user/"
           f"{urllib.parse.quote(article.replace(' ', '_'), safe='')}/daily/{start:%Y%m%d}/{end:%Y%m%d}")
    r = S.get(url, headers={"User-Agent": "shorts-research/1.0 (github.com/s-shorts/space)"}, timeout=20)
    r.raise_for_status()
    v = [i["views"] for i in r.json()["items"]]
    recent, before = sum(v[-3:]) / 3 if v else 0, (sum(v[:-3]) / max(len(v) - 3, 1)) if len(v) > 3 else 0
    return {"daily": v, "recent_avg": int(recent), "before_avg": int(before),
            "rising_ratio": round(recent / before, 2) if before else None}


def channel_stats(path, channel_target, limit):
    rows = []
    for line in Path(path).read_text().splitlines():
        try:
            e = json.loads(line)
        except ValueError:
            continue
        res = e.get("results", {}).get(channel_target)
        if res and res.get("status") == "done" and res.get("id"):
            rows.append((e, res))
    out = []
    for e, res in rows[-limit:]:
        try:
            d = video_details(res["id"])
        except Exception as exc:
            d = {"error": str(exc)}
        hours = None
        if res.get("at"):
            hours = round((published_days(res["at"]) or 0) * 24, 1)
        views = d.get("views")
        out.append({"id": res["id"], "title": e.get("title"), "posted": res.get("at"), "hours_live": hours,
                    "views": views, "likes": d.get("likes"), "comments": d.get("comments"),
                    "views_per_hour": round(views / hours, 1) if views and hours else None,
                    "like_rate": round(d["likes"] / views, 4) if views and d.get("likes") else None})
        time.sleep(0.7)
    good = [o for o in out if o["views"] is not None]
    summary = {}
    if good:
        vs = sorted(o["views"] for o in good)
        summary = {"videos": len(good), "median_views": vs[len(vs) // 2], "max_views": vs[-1],
                   "top5": sorted(good, key=lambda o: -(o["views"] or 0))[:5],
                   "bottom5": sorted(good, key=lambda o: (o["views"] or 0))[:5]}
    return {"videos": out, "summary": summary}


def run(name, fn, results, errors):
    try:
        results[name] = fn()
    except Exception as exc:
        errors[name] = f"{type(exc).__name__}: {exc}"
        traceback.print_exc()


def main():
    req = json.loads(Path("request.json").read_text())
    results, errors = {"id": req.get("id"), "made": NOW.isoformat()}, {}

    yq = req.get("youtube_queries", [])[:12]
    if yq:
        yt = {}
        for q in yq:
            try:
                items = youtube_search(q, shorts=req.get("shorts_only", True))
                # shelf Shorts carry no age/channel: look up the top few
                for it in items[:8]:
                    if it.get("age_days") is None and it.get("id"):
                        try:
                            d = video_details(it["id"])
                            it.update({k: v for k, v in d.items() if v is not None and k != "title"})
                            days = published_days(d["published"]) if d.get("published") else None
                            it["age_days"] = round(days, 1) if days else None
                            if it.get("views") and days:
                                it["views_per_day"] = int(it["views"] / max(days, 0.5))
                        except Exception as exc:
                            it["detail_error"] = str(exc)
                        time.sleep(0.5)
                vs = sorted([i["views"] for i in items if i.get("views")], reverse=True)
                yt[q] = {"results": items, "top_views": vs[:3],
                         "median_views": vs[len(vs) // 2] if vs else None}
            except Exception as exc:
                yt[q] = {"error": f"{type(exc).__name__}: {exc}"}
            time.sleep(1)
        results["youtube"] = yt

    for key, yt_flag in (("youtube_suggest", True), ("google_suggest", False)):
        seeds = req.get("suggest", [])[:12]
        if seeds:
            res = {}
            for s in seeds:
                try:
                    res[s] = suggest(s, yt_flag)
                except Exception as exc:
                    res[s] = {"error": str(exc)}
            results[key] = res

    rq = req.get("reddit_queries", [])[:8]
    if rq:
        rd = {}
        for q in rq:
            try:
                rd[q] = reddit(q)
            except Exception as exc:
                rd[q] = {"error": str(exc)}
            time.sleep(1)
        results["reddit"] = rd

    geos = req.get("trends_geo", ["US", "IN", "GB"])
    if geos:
        results["trends"] = {}
        for g in geos:
            try:
                results["trends"][g] = trends(g)
            except Exception as exc:
                results["trends"][g] = {"error": str(exc)}

    if req.get("wiki_top", True):
        run("wiki_top", wiki_top, results, errors)
    wa = req.get("wiki_articles", [])[:10]
    if wa:
        results["wiki_views"] = {}
        for a in wa:
            try:
                results["wiki_views"][a] = wiki_views(a)
            except Exception as exc:
                results["wiki_views"][a] = {"error": str(exc)}

    if req.get("channel_stats", True) and Path("published.jsonl").is_file():
        run("channel", lambda: channel_stats("published.jsonl", req.get("channel_target", "yt-main"),
                                             req.get("channel_limit", 40)), results, errors)

    results["errors"] = errors
    OUT.mkdir(exist_ok=True)
    (OUT / "results.json").write_text(json.dumps(results, indent=1, ensure_ascii=False))
    print(json.dumps({k: (len(v) if isinstance(v, (list, dict)) else v) for k, v in results.items()}))


if __name__ == "__main__":
    sys.exit(main())
