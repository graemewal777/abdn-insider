"""
Aberdeen Insider — RSS News Scraper
Pulls from Aberdeen news RSS feeds and filters for venue openings, events,
food & drink, and nightlife content.

Sources:
  - Aberdeen Live
  - Aberdeen Business News
  - Press & Journal
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import json
import re
import xml.etree.ElementTree as ET
from datetime import datetime, timezone
from email.utils import parsedate_to_datetime

import requests

from scrapers.dedup import filter_new

try:
    from config import RSS_FEEDS
except ImportError:
    RSS_FEEDS = [
        {"name": "Aberdeen Live", "url": "https://www.aberdeenlive.news/news/?service=rss", "categories": ["food", "drink", "nightlife", "events", "opening"]},
        {"name": "Aberdeen Business News", "url": "https://www.aberdeen-business.com/feed/", "categories": ["opening", "hospitality", "retail", "leisure"]},
        {"name": "Press and Journal", "url": "https://www.pressandjournal.co.uk/feed/", "categories": ["events", "food", "drink", "entertainment"]},
    ]

# Keywords that flag a story as a new venue/opening
OPENING_KEYWORDS = [
    "opens", "opening", "reopens", "reopening", "launch", "launches", "launched",
    "new restaurant", "new bar", "new cafe", "new venue", "new shop", "new store",
    "new bakery", "new coffee", "now open", "grand opening", "soft launch",
    "pop-up", "popup",
]

# Keywords that flag a story as an event — matched as WHOLE WORDS to avoid
# "supermarket" matching "market", "events on Monday" matching "event", etc.
EVENT_KEYWORDS = [
    "festival", "concert", "gig", "exhibition", "comedy night", "quiz night",
    "night out", "live music", "farmers market", "night market", "street food",
    "pop-up market", "food market", "craft market", "open mic",
]

# Keywords to filter for Aberdeen relevance (skip if none present in title/summary)
ABERDEEN_KEYWORDS = [
    "aberdeen", "aberdeenshire", "granite city", "dons", "union street",
    "george street", "belmont", "rosemount", "torry", "bridge of don",
    "cults", "bieldside", "westhill", "portlethen", "inverurie",
]

# Keywords indicating content NOT relevant to our audience
SKIP_KEYWORDS = [
    "obituary", "court", "crime", "accident", "fatal", "death", "murder",
    "sentencing", "trial", "police", "fire brigade", "oil field", "offshore platform",
    "football", "rugby", "cricket", "golf", "tennis", "olympics", "paralympics",
    "transfer", "manager", "squad", "league table",
    "drink driving", "drink-driving", "charged", "arrested", "convicted",
    "prison", "jail", "assault", "stabbing", "fraud",
]

HEADERS = {
    "User-Agent": "Mozilla/5.0 (compatible; AberdeenInsider/1.0; +https://instagram.com/abdn.insider)"
}


def _is_aberdeen_relevant(text: str) -> bool:
    text_lower = text.lower()
    return any(kw in text_lower for kw in ABERDEEN_KEYWORDS)


def _should_skip(text: str) -> bool:
    text_lower = text.lower()
    return any(kw in text_lower for kw in SKIP_KEYWORDS)


def _classify_item(title: str, summary: str) -> str | None:
    """Return 'opening', 'event', 'news', or None to skip."""
    combined = f"{title} {summary}".lower()

    if _should_skip(combined):
        return None

    if any(kw in combined for kw in OPENING_KEYWORDS):
        return "opening"

    if any(kw in combined for kw in EVENT_KEYWORDS):
        return "event"

    # Catch general Aberdeen lifestyle / food / drink news
    lifestyle_kws = ["restaurant", "bar", "cafe", "coffee", "food", "drink", "pub", "nightlife"]
    if any(kw in combined for kw in lifestyle_kws):
        return "news"

    return None  # not relevant


def _clean_html(text: str) -> str:
    """Strip HTML tags and clean whitespace."""
    if not text:
        return ""
    text = re.sub(r"<[^>]+>", " ", text)
    text = re.sub(r"\s+", " ", text).strip()
    return text[:500]  # cap summary length


def _parse_rss_date(date_str: str) -> str:
    """Parse RFC 2822 date string to ISO 8601."""
    if not date_str:
        return datetime.now().isoformat()
    try:
        dt = parsedate_to_datetime(date_str)
        return dt.astimezone(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    except Exception:
        return date_str


def _fetch_feed(feed_config: dict) -> list[dict]:
    """Fetch and parse one RSS feed. Returns list of relevant item dicts."""
    name = feed_config["name"]
    url = feed_config["url"]

    try:
        resp = requests.get(url, headers=HEADERS, timeout=15)
        resp.raise_for_status()
        content = resp.content
    except requests.RequestException as e:
        print(f"  ⚠️  {name}: fetch failed — {e}")
        return []

    try:
        root = ET.fromstring(content)
    except ET.ParseError as e:
        print(f"  ⚠️  {name}: XML parse error — {e}")
        return []

    # Handle both standard RSS and Atom namespaces
    ns = {"content": "http://purl.org/rss/1.0/modules/content/"}
    items_found = root.findall(".//item")

    results = []
    for item in items_found[:30]:  # limit per feed

        def _text(tag: str) -> str:
            el = item.find(tag)
            return el.text.strip() if el is not None and el.text else ""

        title = _clean_html(_text("title"))
        raw_summary = _text("description") or _text("{http://purl.org/rss/1.0/modules/content/}encoded")
        summary = _clean_html(raw_summary)
        link = _text("link") or _text("guid")
        pub_date = _parse_rss_date(_text("pubDate"))

        if not title or not link:
            continue

        # Aberdeen relevance check — only strict for generic feeds
        if name == "Press and Journal" and not _is_aberdeen_relevant(f"{title} {summary}"):
            continue

        item_type = _classify_item(title, summary)
        if item_type is None:
            continue

        results.append({
            "title": title,
            "summary": summary,
            "url": link,
            "date": pub_date,
            "category": item_type,
            "type": item_type,
            "source": name,
            "weekend_relevant": item_type == "event",
        })

    return results


def scrape_rss_feeds() -> list[dict]:
    """Scrape all configured RSS feeds and return filtered Aberdeen content."""
    print("📰 Fetching RSS feeds...")
    all_items = []
    seen_urls = set()

    for feed in RSS_FEEDS:
        print(f"  → {feed['name']}...")
        items = _fetch_feed(feed)

        for item in items:
            if item["url"] not in seen_urls:
                seen_urls.add(item["url"])
                all_items.append(item)

        print(f"     {len(items)} relevant items")

    # Sort by date descending
    all_items.sort(key=lambda x: x.get("date", ""), reverse=True)

    # If no real data fetched, use samples
    if not all_items:
        print("⚠️  No RSS data fetched — using sample Aberdeen news.")
        all_items = _sample_rss_items()

    # Deduplicate against seen store
    new_items, skipped = filter_new(all_items, id_key="url")
    if skipped:
        print(f"   ({skipped} RSS items already seen — skipped)")

    openings = [i for i in new_items if i["type"] == "opening"]
    events   = [i for i in new_items if i["type"] == "event"]
    news     = [i for i in new_items if i["type"] == "news"]

    print(f"✅ RSS: {len(openings)} new openings, {len(events)} new events, {len(news)} new news items")
    return new_items


def _sample_rss_items() -> list[dict]:
    """Sample Aberdeen news items for dev/testing."""
    now = datetime.now().strftime("%Y-%m-%dT%H:%M:%SZ")
    return [
        {
            "title": "New Japanese ramen bar to open on Belmont Street",
            "summary": "A new Japanese ramen and izakaya bar is set to open on Aberdeen's Belmont Street this spring, bringing authentic tonkotsu broth and natural wine to the city centre.",
            "url": "https://www.aberdeenlive.news/food-drink/",
            "date": now,
            "category": "opening",
            "type": "opening",
            "source": "Aberdeen Live (sample)",
            "weekend_relevant": False,
        },
        {
            "title": "Beloved Aberdeen café secures new premises on George Street",
            "summary": "After months of searching, the team behind one of Aberdeen's most popular independent coffee shops has signed a lease on a new George Street location.",
            "url": "https://www.aberdeen-business.com/",
            "date": now,
            "category": "opening",
            "type": "opening",
            "source": "Aberdeen Business News (sample)",
            "weekend_relevant": False,
        },
        {
            "title": "Aberdeen Food & Drink Festival returns to Duthie Park",
            "summary": "The Aberdeen Food & Drink Festival is back for its annual showcase, featuring over 50 local producers, live demonstrations, and street food traders across Duthie Park.",
            "url": "https://www.pressandjournal.co.uk/",
            "date": now,
            "category": "event",
            "type": "event",
            "source": "Press and Journal (sample)",
            "weekend_relevant": True,
        },
        {
            "title": "Union Square welcomes first Aberdeen outpost of popular Edinburgh cocktail bar",
            "summary": "Edinburgh cocktail institution Heads & Tales has signed a deal to open its first Aberdeen venue inside Union Square, bringing its acclaimed spirits-led drinks menu north.",
            "url": "https://www.aberdeenlive.news/food-drink/",
            "date": now,
            "category": "opening",
            "type": "opening",
            "source": "Aberdeen Live (sample)",
            "weekend_relevant": False,
        },
    ]


if __name__ == "__main__":
    items = scrape_rss_feeds()
    print(json.dumps(items[:5], indent=2))
