"""
Aberdeen Insider — Ticketmaster Discovery API Scraper
Pulls Aberdeen events for the coming weekend from the Ticketmaster Discovery API.
Supplements Skiddle — particularly good for larger venue shows (P&J Live, etc).

API docs: https://developer.ticketmaster.com/products-and-docs/apis/discovery-api/v2/
Free tier: 5,000 requests/day
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import json
import requests
from datetime import datetime, timedelta

from scrapers.dedup import filter_new
from scrapers.skiddle import VIBE_TEMPLATES, _get_weekend_dates

try:
    from config import TICKETMASTER_API_KEY
except ImportError:
    TICKETMASTER_API_KEY = os.getenv("TICKETMASTER_API_KEY", "")

TM_BASE_URL = "https://app.ticketmaster.com/discovery/v2/events.json"

# Map Ticketmaster segment/genre names to our categories
SEGMENT_MAP = {
    "Music":          "Live Music",
    "Sports":         "Sport",
    "Arts & Theatre": "Arts",
    "Film":           "Arts",
    "Miscellaneous":  "Other",
    "Comedy":         "Comedy",
}

GENRE_MAP = {
    "Comedy":         "Comedy",
    "Dance/Electronic": "Nightlife",
    "Hip-Hop/Rap":    "Nightlife",
    "Pop":            "Live Music",
    "Rock":           "Live Music",
    "Jazz":           "Live Music",
    "Classical":      "Arts",
    "Theatre":        "Arts",
    "Opera":          "Arts",
    "Food & Drink":   "Food & Drink",
    "Family":         "Family",
}


def _category_from_event(raw: dict) -> str:
    """Derive our category from Ticketmaster classifications."""
    classifications = raw.get("classifications", [])
    if not classifications:
        return "Other"

    cls = classifications[0]
    genre_name    = cls.get("genre",    {}).get("name", "")
    subgenre_name = cls.get("subGenre", {}).get("name", "")
    segment_name  = cls.get("segment", {}).get("name", "")

    # Genre/subgenre first (more specific)
    for name in (genre_name, subgenre_name):
        if name in GENRE_MAP:
            return GENRE_MAP[name]

    # Fall back to segment
    return SEGMENT_MAP.get(segment_name, "Other")


def _parse_event(raw: dict) -> dict:
    """Normalise a Ticketmaster event dict into our standard format."""
    name     = raw.get("name", "Untitled Event")
    category = _category_from_event(raw)

    # Vibe note
    options  = VIBE_TEMPLATES.get(category, VIBE_TEMPLATES["Other"])
    venue_name = ""
    venues = raw.get("_embedded", {}).get("venues", [])
    if venues:
        venue_name = venues[0].get("name", "")
    vibe = options[hash(name + venue_name) % len(options)]

    # Date / time
    dates      = raw.get("dates", {})
    start      = dates.get("start", {})
    date_raw   = start.get("localDate", "")
    time_local = start.get("localTime", "")

    try:
        date_str = datetime.strptime(date_raw, "%Y-%m-%d").strftime("%a %d %b")
    except (ValueError, TypeError):
        date_str = date_raw

    try:
        time_str = datetime.strptime(time_local, "%H:%M:%S").strftime("%I:%M %p").lstrip("0")
    except (ValueError, TypeError):
        time_str = time_local[:5] if time_local else "TBC"

    # Venue / address
    address = ""
    if venues:
        v = venues[0]
        parts = [
            v.get("address", {}).get("line1", ""),
            v.get("city",    {}).get("name", ""),
            v.get("postalCode", ""),
        ]
        address = ", ".join(p for p in parts if p)

    # Price
    price_ranges = raw.get("priceRanges", [])
    if price_ranges:
        min_price = price_ranges[0].get("min", 0)
        try:
            price_val = float(min_price)
            price = f"£{price_val:.0f}+" if price_val > 0 else "Check website"
        except (TypeError, ValueError):
            price = "Check website"
    else:
        price = "Check website"

    # URL — use the Ticketmaster buy page
    url = raw.get("url", "")

    # Image — grab the widest available
    images = raw.get("images", [])
    image_url = ""
    if images:
        widest = max(images, key=lambda i: i.get("width", 0))
        image_url = widest.get("url", "")

    return {
        "name":             name,
        "date":             date_str,
        "date_raw":         date_raw,
        "time":             time_str,
        "venue":            venue_name,
        "address":          address,
        "category":         category,
        "price":            price,
        "url":              url,
        "image_url":        image_url,
        "vibe_note":        vibe,
        "type":             "event",
        "weekend_relevant": True,
        "source":           "ticketmaster",
    }


def scrape_ticketmaster() -> list[dict]:
    """Fetch Aberdeen weekend events from the Ticketmaster Discovery API.

    Returns a list of event dicts, deduped against already-seen events.
    Gracefully returns [] if no API key is set.
    """
    if not TICKETMASTER_API_KEY:
        print("⚠️  No Ticketmaster API key — skipping (set TICKETMASTER_API_KEY in config.py)")
        return []

    friday, sunday = _get_weekend_dates()

    # Ticketmaster uses ISO 8601 with time component
    start_dt = f"{friday}T00:00:00Z"
    end_dt   = f"{sunday}T23:59:59Z"

    params = {
        "apikey":         TICKETMASTER_API_KEY,
        "city":           "Aberdeen",
        "countryCode":    "GB",
        "startDateTime":  start_dt,
        "endDateTime":    end_dt,
        "size":           50,
        "sort":           "relevance,desc",
    }

    try:
        resp = requests.get(TM_BASE_URL, params=params, timeout=15)
        resp.raise_for_status()
        data = resp.json()
    except requests.RequestException as e:
        print(f"⚠️  Ticketmaster API error: {e} — skipping.")
        return []

    embedded = data.get("_embedded", {})
    results  = embedded.get("events", []) if embedded else []

    if not results:
        print(f"ℹ️  Ticketmaster: no events found for {friday} → {sunday}")
        return []

    events = [_parse_event(r) for r in results]
    new_events, skipped = filter_new(events, id_key="url")
    print(f"✅ Ticketmaster: {len(new_events)} new events ({skipped} already seen) for {friday} → {sunday}")
    return new_events


if __name__ == "__main__":
    events = scrape_ticketmaster()
    print(json.dumps(events, indent=2))
