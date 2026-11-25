#!/usr/bin/env python3
"""
Scrape Reddit via Apify — API-backed actors that survive Reddit's 2026 anti-bot block.

Why this exists: the old HTML actor `trudax/reddit-scraper-lite` now gets 403'd by
Reddit. These two actors hit Reddit through an API path and still work (verified 2026-05-31):
  - subreddit listing  -> crawlerbros/reddit-scraper
  - keyword search     -> practicaltools/apify-reddit-api

Token: read from $APIFY_TOKEN, else from the .env file in this skill's folder
(one level up from scripts/). The token is sent in an Authorization header, never
in the URL, and is never printed.

Usage:
  python3 reddit_scrape.py str airbnb                 # top posts this week from 2 subreddits
  python3 reddit_scrape.py ClaudeAI -n 25 -s hot            # 25 hot posts
  python3 reddit_scrape.py -q "serena mcp" -n 10            # keyword search across Reddit
  python3 reddit_scrape.py str --json > out.json            # raw JSON for piping into other tools
"""
import argparse, json, os, sys, urllib.request, urllib.error
from pathlib import Path

SUBREDDIT_ACTOR = "crawlerbros~reddit-scraper"        # subreddit listing mode
SEARCH_ACTOR    = "practicaltools~apify-reddit-api"   # keyword search mode


SKILL_DIR = Path(__file__).resolve().parent.parent
ENV_FILE = SKILL_DIR / ".env"


def load_token() -> str:
    t = os.environ.get("APIFY_TOKEN")
    if t and t.strip():
        return t.strip()
    if ENV_FILE.exists():
        for line in ENV_FILE.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if line.startswith("APIFY_TOKEN="):
                val = line.split("=", 1)[1].strip().strip('"').strip("'")
                if val:
                    return val
    sys.exit(f"ERROR: no APIFY_TOKEN. Set the APIFY_TOKEN env var or put APIFY_TOKEN=... in {ENV_FILE}")


def run_actor(actor: str, payload: dict, token: str) -> list:
    url = f"https://api.apify.com/v2/acts/{actor}/run-sync-get-dataset-items"
    req = urllib.request.Request(
        url, data=json.dumps(payload).encode(),
        headers={"Content-Type": "application/json", "Authorization": f"Bearer {token}"},
    )
    try:
        with urllib.request.urlopen(req, timeout=300) as r:
            return json.loads(r.read())
    except urllib.error.HTTPError as e:
        sys.exit(f"ERROR: Apify {actor} returned HTTP {e.code}: {e.read()[:300].decode(errors='ignore')}")
    except urllib.error.URLError as e:
        sys.exit(f"ERROR: could not reach Apify ({e.reason}). Check your internet connection.")


def normalize(item: dict) -> dict:
    """Flatten the two actors' slightly different field names into one shape."""
    sub = (item.get("subreddit") or item.get("communityName") or item.get("parsedCommunityName") or "").lstrip("/")
    if sub.lower().startswith("r/"):
        sub = sub[2:]
    return {
        "title":     item.get("title") or item.get("postTitle") or "",
        "subreddit": sub,
        "author":    item.get("author") or item.get("username") or "",
        "score":     item.get("upVotes") or item.get("score") or item.get("numberOfUpvotes") or 0,
        "comments":  item.get("numberOfComments") or item.get("numComments") or 0,
        "url":       item.get("url") or item.get("link") or "",
        "text":      (item.get("text") or item.get("body") or item.get("selftext") or "")[:500],
    }


def main() -> None:
    # Windows consoles default to a legacy code page; keep the arrows/dashes from crashing print().
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass
    ap = argparse.ArgumentParser(description="Scrape Reddit via Apify (API-backed, block-resistant).")
    ap.add_argument("subreddits", nargs="*", help="subreddit names, e.g. str airbnb ClaudeAI")
    ap.add_argument("-q", "--search", help="keyword search across Reddit instead of subreddit listing")
    ap.add_argument("-n", "--max", type=int, default=15, help="max posts (default 15)")
    ap.add_argument("-s", "--sort", default=None,
                    choices=["hot", "new", "top", "rising", "relevance"],
                    help="sort (default: top for subreddits, relevance for search)")
    ap.add_argument("-t", "--time", default=None,
                    choices=["hour", "day", "week", "month", "year", "all"],
                    help="time window (default: week for subreddits, month for search)")
    ap.add_argument("--json", action="store_true", help="emit raw normalized JSON")
    args = ap.parse_args()

    if not args.subreddits and not args.search:
        ap.error("give one or more subreddits, or use -q/--search")

    token = load_token()

    if args.search:
        actor = SEARCH_ACTOR
        sort = args.sort or "relevance"
        twindow = args.time or "month"
        payload = {
            "searches": [args.search],
            "sort": sort,
            "time": twindow,
            "maxItems": args.max,
            "skipComments": True,
            "skipCommunity": True,
            "skipUserPosts": True,
        }
        label = f'search "{args.search}"'
    else:
        actor = SUBREDDIT_ACTOR
        sort = args.sort or "top"
        twindow = args.time or "week"
        payload = {
            "subreddits": args.subreddits,
            "maxPosts": args.max,
            "sort": sort,
            "timeFilter": twindow,
        }
        label = "r/" + ", r/".join(args.subreddits)

    rows = [normalize(x) for x in run_actor(actor, payload, token) if isinstance(x, dict)]
    # drop community/profile rows that have no title
    rows = [r for r in rows if r["title"]]

    if args.json:
        print(json.dumps(rows, indent=2))
        return

    if not rows:
        print(f"No results for {label}. (Try a different sort/time, or -q search mode.)")
        return

    print(f"\n# Reddit — {label}  ({len(rows)} posts, sort={sort}, time={twindow})\n")
    for r in rows:
        print(f"[{r['score']}↑ {r['comments']}c] r/{r['subreddit']} — {r['title']}")
        if r["url"]:
            print(f"    {r['url']}")


if __name__ == "__main__":
    main()
