"""
Aberdeen Insider — Weekly Pipeline Runner
Run this every Friday morning to generate the week's content.

Usage:
    python3 scheduler.py              # Full pipeline (scrape + generate)
    python3 scheduler.py --scrape     # Scrape only
    python3 scheduler.py --generate   # Generate content only
    python3 scheduler.py --reset-seen # Clear dedup store (dev only)
"""

import argparse
import json
from datetime import datetime
from pathlib import Path


def run_scrapers():
    """Run all scrapers, deduplicate, and save combined_weekly.json."""
    print("🔍 Running scrapers...\n")

    from scrapers.skiddle import scrape_skiddle
    from scrapers.ticketmaster import scrape_ticketmaster
    from scrapers.rss_scraper import scrape_rss_feeds
    from scrapers.google_places import enrich_venues
    from scrapers.dedup import seen_count

    skiddle_events      = scrape_skiddle()
    ticketmaster_events = scrape_ticketmaster()
    news              = scrape_rss_feeds()

    # RSS events (gigs, festivals from news feeds) normalised to event format
    rss_events = []
    for item in news:
        if item.get("type") == "event":
            raw_date = item.get("date", "")
            try:
                date_display = datetime.fromisoformat(
                    raw_date.replace("Z", "+00:00")
                ).strftime("%a %d %b")
            except (ValueError, AttributeError):
                date_display = raw_date[:10]

            rss_events.append({
                **item,
                "name":  item.get("title", item.get("name", "")),
                "venue": item.get("source", ""),
                "date":  date_display,
                "price": item.get("price", ""),
                "time":  "",
            })

    # Skiddle first (highest quality), then Ticketmaster, then RSS
    all_events = skiddle_events + ticketmaster_events + rss_events

    # Fill in any missing venue addresses via Google Places
    all_events = enrich_venues(all_events)

    combined = {
        "scraped_at": datetime.now().isoformat(),
        "week_of":    datetime.now().strftime("%Y-%m-%d"),
        "events":     all_events,
        "openings":   [item for item in news if item.get("type") == "opening"],
        "news":       [item for item in news if item.get("type") == "news"],
    }

    output_path = Path("data/combined_weekly.json")
    output_path.parent.mkdir(exist_ok=True)
    with open(output_path, "w") as f:
        json.dump(combined, f, indent=2)

    print(f"\n📦 Saved to {output_path}")
    print(f"   {len(skiddle_events)} Skiddle · {len(ticketmaster_events)} Ticketmaster · {len(rss_events)} RSS events")
    print(f"   {len(combined['openings'])} openings · {len(combined['news'])} news")
    print(f"   Dedup store: {seen_count()} items tracked total")
    return combined


def run_generators(data=None):
    """Generate carousel, caption and link-in-bio from combined data."""
    print("\n🎨 Generating content...\n")

    if data is None:
        with open("data/combined_weekly.json") as f:
            data = json.load(f)

    from generators.carousel import generate_carousel
    from generators.caption import generate_caption
    from generators.linkinbio import generate_linkinbio

    carousel_dir = generate_carousel(data)
    caption      = generate_caption(data)
    linkinbio    = generate_linkinbio(data)

    print("\n" + "─" * 52)
    print("📝  INSTAGRAM CAPTION — COPY AND PASTE BELOW:")
    print("─" * 52)
    print(caption)
    print("─" * 52)
    print(f"({len(caption)} chars — limit is 2,200)\n")

    return carousel_dir


def main():
    parser = argparse.ArgumentParser(description="Aberdeen Insider Pipeline")
    parser.add_argument("--scrape",     action="store_true", help="Run scrapers only")
    parser.add_argument("--generate",   action="store_true", help="Run generators only")
    parser.add_argument("--reset-seen", action="store_true", help="Clear dedup store (dev only)")
    args = parser.parse_args()

    print(f"\n🏙️  Aberdeen Insider — {datetime.now().strftime('%A %d %B %Y')}\n")

    if args.reset_seen:
        from scrapers.dedup import clear_all
        clear_all()
        print("Dedup store cleared. Run again without --reset-seen to scrape fresh.")
        return

    if args.scrape:
        run_scrapers()
    elif args.generate:
        run_generators()
    else:
        data = run_scrapers()
        carousel_dir = run_generators(data)
        print("✨ Done!")
        print(f"   → 📸 Carousel PNGs: {carousel_dir}/")
        print("   → 📋 Paste the caption above into Instagram")
        print("   → 🔗 Update your bio link to: output/newsletters/")


if __name__ == "__main__":
    main()
