# -*- coding: utf-8 -*-
"""YouTube Data API v3 search helper for the YouTube_Solutions deliverable.

Finds real, relevance-ranked candidate videos for a question — a direct YouTube
index query (not scraped web search), so coverage is far better than WebSearch.

KEY: read from env YT_API_KEY, else from the file tools/.yt_api_key (one line).
     The key is a secret: keep it out of anything published/shared. This script
     sends it ONLY to googleapis.com (its sole purpose) and never prints it.

Usage:
  python yt_search.py "tangent to circle condition slope JEE class 11"
  python yt_search.py --max 8 --hindi "vruttachi sparshika ...."     # relevanceLanguage=hi
  python yt_search.py --json "..."     # machine-readable list for agents

Each result: {id, title, channel, embeddable, live(oembed 200/401)}.
search.list costs 100 quota units; free tier = 10,000/day = ~100 searches/day.
"""
import io, json, os, sys, urllib.parse, urllib.request, urllib.error

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
HERE = os.path.dirname(os.path.abspath(__file__))

def load_key():
    k = os.environ.get("YT_API_KEY", "").strip()
    if k:
        return k
    p = os.path.join(HERE, ".yt_api_key")
    if os.path.isfile(p):
        return open(p, encoding="utf-8").read().strip()
    sys.exit("No API key. Set env YT_API_KEY or create tools/.yt_api_key (one line).")

def _get(url):
    req = urllib.request.Request(url, headers={"User-Agent": "icad-youtube-solutions/1.0"})
    with urllib.request.urlopen(req, timeout=20) as r:
        return r.status, json.loads(r.read().decode("utf-8", "replace"))

def oembed_status(vid):
    url = "https://www.youtube.com/oembed?url=https://www.youtube.com/watch?v=%s&format=json" % vid
    try:
        with urllib.request.urlopen(urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"}), timeout=15) as r:
            return r.status
    except urllib.error.HTTPError as e:
        return e.code
    except Exception:
        return "ERR"

def search(query, key, maxn=10, lang="en"):
    params = {
        "part": "snippet", "type": "video", "q": query,
        "maxResults": str(maxn), "relevanceLanguage": lang,
        "safeSearch": "strict", "key": key,
    }
    url = "https://www.googleapis.com/youtube/v3/search?" + urllib.parse.urlencode(params)
    try:
        _, data = _get(url)
    except urllib.error.HTTPError as e:
        body = e.read().decode("utf-8", "replace")
        sys.exit("YouTube API error %s: %s" % (e.code, body[:300]))
    out = []
    for it in data.get("items", []):
        vid = it.get("id", {}).get("videoId")
        sn = it.get("snippet", {})
        if not vid:
            continue
        out.append({"id": vid, "title": sn.get("title", ""),
                    "channel": sn.get("channelTitle", "")})
    return out

def main():
    args = sys.argv[1:]
    maxn, lang, as_json, verify = 10, "en", False, True
    q = []
    i = 0
    while i < len(args):
        a = args[i]
        if a == "--max":
            maxn = int(args[i + 1]); i += 2
        elif a == "--hindi":
            lang = "hi"; i += 1
        elif a == "--json":
            as_json = True; i += 1
        elif a == "--no-verify":
            verify = False; i += 1
        else:
            q.append(a); i += 1
    query = " ".join(q).strip()
    if not query:
        sys.exit('Usage: python yt_search.py "<query>"  [--max N] [--hindi] [--json] [--no-verify]')
    key = load_key()
    res = search(query, key, maxn, lang)
    if verify:
        for r in res:
            r["oembed"] = oembed_status(r["id"])   # 200 public / 401 embed-off / 403-404 dead
    if as_json:
        print(json.dumps(res, ensure_ascii=False, indent=1))
    else:
        print('query: %s   (%d results)' % (query, len(res)))
        for r in res:
            tag = {200: "live", 401: "live(no-embed)"}.get(r.get("oembed"), "DEAD?") if verify else ""
            print("  %-11s %-15s %s  | %s" % (r["id"], tag, r["title"][:70], r["channel"][:24]))

if __name__ == "__main__":
    main()
