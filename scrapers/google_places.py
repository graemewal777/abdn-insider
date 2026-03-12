"""
Aberdeen Insider — Google Places Venue Enricher
Fills in missing address data for events using the Google Places API.

Setup:
  1. Go to console.cloud.google.com → enable "Places API"
  2. Create an API key → paste into config.py as GOOGLE_PLACES_API_KEY
  3. Restrict the key to "Places API" for safety

Usage:
  enrich_venues(events)  — mutates events in place, fills blank addresses

Costs roughly £0.02–£0.05 per week (5–15 venue lookups at $17/1000 requests).
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import time
import requests

try:
    from config import GOOGLE_PLACES_API_KEY
except ImportError:
    GOOGLE_PLACES_API_KEY = os.getenv("GOOGLE_PLACES_API_KEY", "")

PLACES_BASE = "https://maps.googleapis.com/maps/api/place"


def _find_venue(venue_name: str) -> str:
    """
    Look up a venue in Aberdeen using Places Text Search.
    Returns the formatted address string, or "" if not found.
    """
    params = {
        "query": f"{venue_name} Aberdeen Scotland",
        "key":   GOOGLE_PLACES_API_KEY,
        "type":  "establishment",
    }
    try:
        resp = requests.get(
            f"{PLACES_BASE}/textsearch/json",
            params=params,
            timeout=10,
        )
        resp.raise_for_status()
        results = resp.json().get("results", [])
        if not results:
            return ""

        place = results[0]
        full_addr = place.get("formatted_address", "")

        # "Blue Lamp, 121 Gallowgate, Aberdeen AB25 1BU, UK"
        # Strip trailing ", UK" / ", United Kingdom" for cleaner display
        for suffix in (", UK", ", United Kingdom"):
            if full_addr.endswith(suffix):
                full_addr = full_addr[: -len(suffix)]
                break

        # Only return if the address actually contains Aberdeen
        if "Aberdeen" not in full_addr and "Aberdeenshire" not in full_addr:
            return ""

        return full_addr

    except requests.RequestException:
        return ""


def enrich_venues(events: list[dict]) -> list[dict]:
    """
    For each event that has a venue name but no address, look up the address
    via Google Places. Mutates and returns the events list.
    Skips events that already have an address.
    """
    if not GOOGLE_PLACES_API_KEY:
        print("⚠️  No Google Places API key — skipping venue enrichment (set GOOGLE_PLACES_API_KEY in config.py)")
        return events

    enriched = 0
    for event in events:
        venue   = event.get("venue", "").strip()
        address = event.get("address", "").strip()

        if not venue or address:
            continue  # skip if no venue name, or address already populated

        found = _find_venue(venue)
        if found:
            event["address"] = found
            enriched += 1

        time.sleep(0.15)  # stay well within rate limits (~400ms between calls)

    if enriched:
        print(f"✅ Google Places: filled {enriched} missing venue addresses")
    else:
        print("✅ Google Places: no missing addresses to fill")

    return events


if __name__ == "__main__":
    import json
    # Quick test — swap in your own key in config.py
    test_events = [
        {"name": "Test gig",    "venue": "Tunnels Aberdeen",  "address": ""},
        {"name": "Comedy night","venue": "Breakneck Comedy",  "address": ""},
        {"name": "Already set", "venue": "The Lemon Tree",    "address": "5 West North St"},
    ]
    result = enrich_venues(test_events)
    print(json.dumps(result, indent=2))
