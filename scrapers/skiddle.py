"""
Aberdeen Insider — Skiddle Events Scraper
Pulls Aberdeen events for the coming weekend (Fri–Sun) from the Skiddle API.
Falls back to sample data if no API key is set (for development/testing).

Skiddle API docs: https://www.skiddle.com/api/
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import json
import requests
from datetime import datetime, timedelta
from pathlib import Path

from scrapers.dedup import filter_new

try:
    from config import SKIDDLE_API_KEY, SKIDDLE_AFFILIATE_ID, CITY_LAT, CITY_LNG, CITY_RADIUS_KM
except ImportError:
    SKIDDLE_API_KEY = ""
    SKIDDLE_AFFILIATE_ID = ""
    CITY_LAT = 57.1497
    CITY_LNG = -2.0943
    CITY_RADIUS_KM = 10

SKIDDLE_BASE_URL = "https://www.skiddle.com/api/v1/events/search/"

# Event name prefixes that indicate logistics listings, not events to promote
SKIP_NAME_PREFIXES = ("bus to ", "coach to ", "return bus", "transport to")

# Map Skiddle event codes to our categories
EVENTCODE_MAP = {
    "CLUB": "Nightlife",
    "LIVE": "Live Music",
    "FEST": "Festival",
    "COMEDY": "Comedy",
    "THEATRE": "Arts",
    "BARPUB": "Food & Drink",
    "SPORT": "Sport",
    "ARTS": "Arts",
    "EXHIB": "Arts",
    "KIDS": "Family",
    "FILM": "Arts",
    "OTHER": "Other",
}

VIBE_TEMPLATES = {
    "Nightlife": [
        "Aberdeen nights don't miss. Get tickets before it sells out.",
        "This one fills up fast — the kind of night people are still talking about Monday.",
        "Don't leave it too late. Nightlife in this city moves quick.",
        "Classic Aberdeen big night. You know you want to.",
        "Grab tickets now — standing at the door hoping is not a vibe.",
        "This city goes hard when it goes out. Get in early.",
        "One of those nights. Secure your ticket while they're still moving.",
    ],
    "Live Music": [
        "Live always beats a playlist. Get in and experience it properly.",
        "Worth leaving the house for. Secure your spot before it sells out.",
        "Gigs in Aberdeen hit different when the room's full. Don't miss it.",
        "Tickets going. You'll regret watching it on someone's story.",
        "One of the better live shows coming through Aberdeen. Book it.",
        "This one will sell. Don't be the person who finds out too late.",
        "See it live — limited tickets, limited excuses.",
    ],
    "Festival": [
        "Aberdeen festival energy is rare — don't sleep on this one.",
        "Festivals in the North hit different. Get your ticket now.",
        "These sell out faster than you think. Early bird wins here.",
        "Proper outdoor Aberdeen energy. Grab tickets before they're gone.",
        "Festival season. The forecast can do one — this is happening.",
    ],
    "Comedy": [
        "Aberdeen's comedy scene is criminally underrated. This one's worth booking.",
        "Quality night out — laughing beats doomscrolling every time. Get a ticket.",
        "Good comics come through Aberdeen more than people realise. Book it.",
        "Guaranteed good evening. Grab a couple of tickets and make it a proper night.",
        "These comedy nights fill up. Don't find out the hard way.",
    ],
    "Arts": [
        "Proper culture in Aberdeen. Worth the ticket price.",
        "Different kind of Friday night — in the best way. Book it.",
        "The kind of thing you'll actually be glad you went to.",
        "Aberdeen's arts scene surprises people. This one's a good reason to find out.",
        "Culture fix. Tickets available — for now.",
    ],
    "Food & Drink": [
        "Eat well, drink well — that's the whole plan. Get booked in.",
        "Food events in Aberdeen are getting properly good. Reserve your spot.",
        "The kind of thing to book before asking if anyone wants to come.",
        "Worth it. Get a table before it's full.",
        "Aberdeen food scene is having a moment. This proves it.",
    ],
    "Sport": [
        "Get down and see it live — always better in the stands.",
        "Local sport hits different when you're actually there.",
        "Grab a ticket and support something real in Aberdeen.",
    ],
    "Family": [
        "Perfect excuse to get out with the wee ones. Book ahead.",
        "Family-friendly and actually good. Rare combo. Grab tickets.",
        "Get the kids out — this one's worth the effort.",
    ],
    "Other": [
        "Worth a look — don't let it pass you by.",
        "One to check out. Tickets available now.",
        "Might just be the best thing you do this weekend.",
    ],
}


def _get_weekend_dates():
    """Return (friday_str, sunday_str) for the nearest upcoming weekend."""
    today = datetime.now()
    days_until_friday = (4 - today.weekday()) % 7  # weekday 4 = Friday
    if days_until_friday == 0 and today.hour >= 20:
        days_until_friday = 7  # already late Friday, skip to next
    friday = today + timedelta(days=days_until_friday)
    sunday = friday + timedelta(days=2)
    return friday.strftime("%Y-%m-%d"), sunday.strftime("%Y-%m-%d")


def _build_affiliate_url(base_url: str) -> str:
    if not base_url:
        return ""
    if not SKIDDLE_AFFILIATE_ID:
        return base_url
    sep = "&" if "?" in base_url else "?"
    return f"{base_url}{sep}sktag={SKIDDLE_AFFILIATE_ID}"


def _parse_event(raw: dict) -> dict:
    event_code = raw.get("EventCode", "OTHER").upper()
    category = EVENTCODE_MAP.get(event_code, "Other")
    options = VIBE_TEMPLATES.get(category, ["Worth checking out."])
    # Pick a variant deterministically from the event name so every event
    # gets a different line, but the same event always gets the same line.
    event_name = raw.get("eventname", raw.get("EventName", ""))
    venue_name = raw.get("venue", {}).get("name", "") if isinstance(raw.get("venue"), dict) else raw.get("venue", "")
    vibe = options[hash(event_name + venue_name) % len(options)]

    # Price — prefer ticketpricing.minPrice (real data); MinPrice is often null
    TICKETED_CODES = {"CLUB", "LIVE", "FEST", "COMEDY", "THEATRE", "FILM", "KIDS", "ARTS", "EXHIB", "SPORT"}
    pricing     = raw.get("ticketpricing") or {}
    min_price   = pricing.get("minPrice") if pricing else raw.get("MinPrice", 0)
    has_tickets = raw.get("tickets", False)
    try:
        price_val = float(min_price) if min_price is not None else 0.0
        if price_val == 0:
            if not has_tickets:
                price = "Free"
            elif event_code in TICKETED_CODES:
                price = "Check website"
            else:
                price = "Free"
        else:
            price = f"£{price_val:.0f}+"
    except (TypeError, ValueError):
        price = "Check website"

    # Time — prefer openingtimes.doorsopen (actual door time)
    doors_open  = raw.get("openingtimes", {}).get("doorsopen", "")
    start_time  = raw.get("starttime", "") or raw.get("StartTime", "")
    time_source = doors_open or start_time
    try:
        if ":" in time_source and len(time_source) <= 5:
            # HH:MM format from openingtimes
            time_str = datetime.strptime(time_source, "%H:%M").strftime("%I:%M %p").lstrip("0")
        else:
            time_str = datetime.strptime(time_source, "%Y-%m-%d %H:%M:%S").strftime("%I:%M %p").lstrip("0")
    except (ValueError, TypeError):
        time_str = time_source[:5] if time_source else "TBC"

    # Date — use ISO startdate if available (more accurate than date field).
    # For multi-day events (e.g. Comic Con) show a range like "Sat 14–Sun 15 Mar".
    event_date = raw.get("date", "") or raw.get("Date", "")
    startdate_iso = raw.get("startdate", "")
    enddate_iso   = raw.get("enddate", "")

    try:
        start_dt = datetime.fromisoformat(startdate_iso.replace("Z", "+00:00"))
        end_dt   = datetime.fromisoformat(enddate_iso.replace("Z", "+00:00"))
        # Use the actual start date (not the search minDate artefact)
        event_date = start_dt.strftime("%Y-%m-%d")
        span_days  = (end_dt.date() - start_dt.date()).days
        if span_days >= 1:
            # Multi-day: show "Sat 14–Sun 15 Mar" (omit repeated month)
            start_label = start_dt.strftime("%a %-d")
            end_label   = end_dt.strftime("%a %-d %b")
            date_str    = f"{start_label}–{end_label}"
        else:
            date_str = start_dt.strftime("%a %d %b")
    except (ValueError, TypeError, AttributeError):
        try:
            date_str = datetime.strptime(event_date, "%Y-%m-%d").strftime("%a %d %b")
        except (ValueError, TypeError):
            date_str = event_date

    event_url = raw.get("link", "") or raw.get("eventurl", "")

    return {
        "name": raw.get("eventname", raw.get("EventName", "Untitled Event")),
        "date": date_str,
        "date_raw": event_date,
        "time": time_str,
        "venue": raw.get("venue", {}).get("name", "") if isinstance(raw.get("venue"), dict) else raw.get("venue", "TBC"),
        "address": raw.get("venue", {}).get("address", "") if isinstance(raw.get("venue"), dict) else "",
        "category": category,
        "price": price,
        "url": _build_affiliate_url(event_url),
        "image_url": raw.get("largeimageurl", raw.get("imageurl", "")),
        "vibe_note": vibe,
        "type": "event",
        "weekend_relevant": True,
        "source": "skiddle",
    }


def scrape_skiddle() -> list[dict]:
    """Fetch Aberdeen weekend events from the Skiddle API.

    Returns a list of event dicts. Falls back to sample data if no API key.
    """
    friday, sunday = _get_weekend_dates()

    if not SKIDDLE_API_KEY:
        print("⚠️  No Skiddle API key set — using sample Aberdeen events.")
        sample = _sample_events(friday, sunday)
        new_events, skipped = filter_new(sample, id_key="url")
        if skipped:
            print(f"   ({skipped} sample events already seen this week — skipped)")
        return new_events

    params = {
        "api_key": SKIDDLE_API_KEY,
        "latitude": CITY_LAT,
        "longitude": CITY_LNG,
        "radius": CITY_RADIUS_KM,
        "minDate": friday,
        "maxDate": sunday,
        "order": "pop",          # popularity order
        "limit": 20,
        "description": 1,
    }

    try:
        resp = requests.get(SKIDDLE_BASE_URL, params=params, timeout=15)
        resp.raise_for_status()
        data = resp.json()
    except requests.RequestException as e:
        print(f"⚠️  Skiddle API error: {e} — falling back to sample data.")
        return _sample_events(friday, sunday)

    results = data.get("results", [])
    if not results:
        print("⚠️  Skiddle returned no results — falling back to sample data.")
        sample = _sample_events(friday, sunday)
        new_events, skipped = filter_new(sample, id_key="url")
        return new_events

    # Pre-filter: drop cancelled events and transport/logistics listings
    filtered, dropped = [], 0
    for r in results:
        if str(r.get("cancelled", "0")) != "0":
            print(f"   ❌ Cancelled — skipping: {r.get('eventname','')}")
            dropped += 1
            continue
        name_lower = r.get("eventname", "").lower()
        if any(name_lower.startswith(p) for p in SKIP_NAME_PREFIXES):
            print(f"   🚌 Transport listing — skipping: {r.get('eventname','')}")
            dropped += 1
            continue
        filtered.append(r)

    events = [_parse_event(r) for r in filtered]
    new_events, skipped = filter_new(events, id_key="url")
    print(f"✅ Skiddle: {len(new_events)} new events ({skipped} already seen, {dropped} filtered) for {friday} → {sunday}")
    return new_events


def _sample_events(friday: str, sunday: str) -> list[dict]:
    """Realistic sample Aberdeen events for dev/testing when no API key."""
    friday_fmt = datetime.strptime(friday, "%Y-%m-%d").strftime("%a %d %b")
    saturday_fmt = (datetime.strptime(friday, "%Y-%m-%d") + timedelta(days=1)).strftime("%a %d %b")
    sunday_fmt = datetime.strptime(sunday, "%Y-%m-%d").strftime("%a %d %b")
    saturday_raw = (datetime.strptime(friday, "%Y-%m-%d") + timedelta(days=1)).strftime("%Y-%m-%d")

    return [
        {
            "name": "Aberdeen Jazz Festival: Late Night Set",
            "date": friday_fmt,
            "date_raw": friday,
            "time": "9:00 PM",
            "venue": "The Blue Lamp",
            "address": "121 Gallowgate, Aberdeen AB25 1BU",
            "category": "Live Music",
            "price": "£12",
            "url": "https://www.skiddle.com/whats-on/Aberdeen/",
            "image_url": "",
            "vibe_note": "The Blue Lamp does jazz right. Intimate, sweaty, worth every penny.",
            "type": "event",
            "weekend_relevant": True,
            "source": "skiddle_sample",
        },
        {
            "name": "Club Tropicana — 80s & 90s Night",
            "date": friday_fmt,
            "date_raw": friday,
            "time": "10:00 PM",
            "venue": "Tunnels",
            "address": "Carnegie's Brae, Aberdeen AB11 6JH",
            "category": "Nightlife",
            "price": "£8",
            "url": "https://www.skiddle.com/whats-on/Aberdeen/",
            "image_url": "",
            "vibe_note": "Tunnels basement is a proper Aberdeen institution. Don't overthink it.",
            "type": "event",
            "weekend_relevant": True,
            "source": "skiddle_sample",
        },
        {
            "name": "Aberdeen Farmers Market",
            "date": saturday_fmt,
            "date_raw": saturday_raw,
            "time": "9:00 AM",
            "venue": "Castlegate, Aberdeen City Centre",
            "address": "Castlegate, Aberdeen AB11",
            "category": "Food & Drink",
            "price": "Free",
            "url": "https://www.skiddle.com/whats-on/Aberdeen/",
            "image_url": "",
            "vibe_note": "Proper local produce. Get there before the good bread sells out.",
            "type": "event",
            "weekend_relevant": True,
            "source": "skiddle_sample",
        },
        {
            "name": "Stand-Up Comedy: New Acts Night",
            "date": saturday_fmt,
            "date_raw": saturday_raw,
            "time": "7:30 PM",
            "venue": "The Lemon Tree",
            "address": "5 West North St, Aberdeen AB24 5AT",
            "category": "Comedy",
            "price": "£10",
            "url": "https://www.skiddle.com/whats-on/Aberdeen/",
            "image_url": "",
            "vibe_note": "Lemon Tree new acts nights are hit or miss — that's the fun of it.",
            "type": "event",
            "weekend_relevant": True,
            "source": "skiddle_sample",
        },
        {
            "name": "Sunday Session: Local DJs",
            "date": sunday_fmt,
            "date_raw": sunday,
            "time": "3:00 PM",
            "venue": "Krakatoa",
            "address": "4 Trinity Quay, Aberdeen AB11 5AA",
            "category": "Nightlife",
            "price": "Free",
            "url": "https://www.skiddle.com/whats-on/Aberdeen/",
            "image_url": "",
            "vibe_note": "Sunday session by the harbour. Easy vibes, local selectors.",
            "type": "event",
            "weekend_relevant": True,
            "source": "skiddle_sample",
        },
    ]


if __name__ == "__main__":
    events = scrape_skiddle()
    print(json.dumps(events, indent=2))
