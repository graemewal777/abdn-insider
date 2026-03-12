"""
Aberdeen Insider — Eventbrite Events Scraper
Supplements Skiddle with Aberdeen weekend events from Eventbrite.

Setup:
  1. Create an account at eventbrite.com
  2. Go to eventbrite.com/account-settings/apps → create a new app
  3. Copy the "Private token" → paste into config.py as EVENTBRITE_API_KEY

Output: list of event dicts in the standard Aberdeen Insider format.
"""

import os
import requests
from datetime import datetime, timedelta

from scrapers.dedup import filter_new
from scrapers.skiddle import VIBE_TEMPLATES  # reuse the same vibe note bank

try:
    from config import EVENTBRITE_API_KEY, CITY_LAT, CITY_LNG, CITY_RADIUS_KM
except ImportError:
    EVENTBRITE_API_KEY = os.getenv("EVENTBRITE_API_KEY", "")
    CITY_LAT = 57.1497
    CITY_LNG = -2.0943
    CITY_RADIUS_KM = 10

EVENTBRITE_BASE = "https://www.eventbriteapi.com/v3"

# Eventbrite category IDs we want (excludes Business, Science, Charity, Politics)
CATEGORY_MAP = {
    "103": "Live Music",    # Music
    "105": "Arts",          # Performing & Visual Arts
    "104": "Arts",          # Film, Media & Entertainment
    "110": "Food & Drink",  # Food & Drink
    "108": "Sport",         # Sports & Fitness
    "115": "Other",         # Hobbies & Special Interest
    "109": "Other",         # Travel & Outdoor
    "111": "Other",         # Community & Culture
    "199": "Other",         # Other
}

INCLUDED_CATEGORY_IDS = set(CATEGORY_MAP.keys())


def _get_weekend_dates() -> tuple[str, str]:
    """Return (friday_iso, sunday_iso) for the nearest upcoming weekend."""
    today = datetime.now()
    days_to_fri = (4 - today.weekday()) % 7
    if days_to_fri == 0 and today.hour >= 20:
        days_to_fri = 7
    friday = today + timedelta(days=days_to_fri)
    sunday = friday + timedelta(days=2)
    return (
        friday.strftime("%Y-%m-%dT00:00:00"),
        sunday.strftime("%Y-%m-%dT23:59:59"),
    )


def _pick_vibe(category: str, name: str, venue: str) -> str:
    """Deterministically pick a vibe note from the template bank."""
    options = VIBE_TEMPLATES.get(category, VIBE_TEMPLATES["Other"])
    return options[hash(name + venue) % len(options)]


def _parse_event(raw: dict) -> dict | None:
    """Map an Eventbrite event dict to our standard format. Returns None to skip."""
    try:
        name = (raw.get("name") or {}).get("text", "").strip()
        if not name:
            return None

        # Date + time
        start       = raw.get("start") or {}
        start_local = start.get("local", "")
        date_display = time_display = date_raw = ""
        if start_local:
            try:
                dt           = datetime.strptime(start_local[:16], "%Y-%m-%dT%H:%M")
                date_display = dt.strftime("%a %d %b")
                time_display = dt.strftime("%I:%M %p").lstrip("0")
                date_raw     = dt.strftime("%Y-%m-%d")
            except ValueError:
                date_display = start_local[:10]

        # Venue — embedded when expand=venue is used
        venue_data   = raw.get("venue") or {}
        venue_name   = venue_data.get("name", "")
        address_data = venue_data.get("address") or {}
        city         = address_data.get("city", "")

        # Hard filter: skip anything not in Aberdeen
        if city and city.lower() not in ("aberdeen", "aberdeen city"):
            return None

        address = address_data.get("localized_address_display", "")

        # Price
        is_free = raw.get("is_free", False)
        if is_free:
            price = "Free"
        else:
            ticket_avail = raw.get("ticket_availability") or {}
            min_price    = ticket_avail.get("minimum_ticket_price") or {}
            major_value  = min_price.get("major_value")
            try:
                val   = float(major_value) if major_value else 0
                price = f"£{val:.0f}+" if val > 0 else "Check website"
            except (ValueError, TypeError):
                price = "Check website"

        cat_id   = str(raw.get("category_id") or "")
        category = CATEGORY_MAP.get(cat_id, "Other")

        logo    = raw.get("logo") or {}
        img_url = logo.get("url", "") if logo else ""

        return {
            "name":             name,
            "date":             date_display,
            "date_raw":         date_raw,
            "time":             time_display,
            "venue":            venue_name,
            "address":          address,
            "category":         category,
            "price":            price,
            "url":              raw.get("url", ""),
            "image_url":        img_url,
            "vibe_note":        _pick_vibe(category, name, venue_name),
            "type":             "event",
            "weekend_relevant": True,
            "source":           "eventbrite",
        }

    except Exception:
        return None


def scrape_eventbrite() -> list[dict]:
    """Fetch Aberdeen weekend events from Eventbrite. Returns list of event dicts."""

    if not EVENTBRITE_API_KEY:
        print("⚠️  No Eventbrite API key — skipping (set EVENTBRITE_API_KEY in config.py)")
        return []

    date_from, date_to = _get_weekend_dates()
    headers = {"Authorization": f"Bearer {EVENTBRITE_API_KEY}"}

    params = {
        "location.latitude":      CITY_LAT,
        "location.longitude":     CITY_LNG,
        "location.within":        f"{CITY_RADIUS_KM}km",
        "start_date.range_start": date_from,
        "start_date.range_end":   date_to,
        "expand":                 "venue,ticket_availability,logo",
        "page_size":              50,
    }

    try:
        resp = requests.get(
            f"{EVENTBRITE_BASE}/events/search/",
            headers=headers,
            params=params,
            timeout=15,
        )
        resp.raise_for_status()
        data = resp.json()
    except requests.RequestException as e:
        print(f"⚠️  Eventbrite request failed: {e} — skipping")
        return []

    raw_events = data.get("events", [])

    events = []
    for raw in raw_events:
        cat_id = str(raw.get("category_id") or "")
        if cat_id and cat_id not in INCLUDED_CATEGORY_IDS:
            continue
        parsed = _parse_event(raw)
        if parsed:
            events.append(parsed)

    new_events, skipped = filter_new(events, id_key="url")
    print(f"✅ Eventbrite: {len(new_events)} new Aberdeen events ({skipped} already seen)")
    return new_events


if __name__ == "__main__":
    import json
    events = scrape_eventbrite()
    print(json.dumps(events, indent=2, default=str))
