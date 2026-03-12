"""
Aberdeen Insider — Instagram Caption Generator
Produces a ready-to-post caption with the week's events, new openings,
and full hashtag set. Keeps the tone sharp and local.

Output: printed to console + saved alongside the carousel HTML.
"""

import json
from datetime import datetime
from pathlib import Path

try:
    from config import HASHTAGS, INSTAGRAM_HANDLE
except ImportError:
    HASHTAGS = [
        "#aberdeen", "#aberdeenscotland", "#aberdeenevents",
        "#thingstodoaberdeen", "#aberdeenlife", "#weekendinaberdeen",
        "#abdn", "#aberdeenfood", "#aberdeennightlife", "#visitaberdeen"
    ]
    INSTAGRAM_HANDLE = "@abdn.insider"

# One-line hooks — rotated by week number so it never repeats back-to-back
HOOKS = [
    "Your Aberdeen weekend, sorted. 📍",
    "Don't waste your weekend. Here's what's on. 📍",
    "Aberdeen's actually got things going on this weekend. 📍",
    "This is your sign to do something decent this weekend. 📍",
    "Five things worth leaving the house for this weekend. 📍",
    "Aberdeen weekend picks — no filler, just the good stuff. 📍",
    "Here's your Aberdeen weekend in five moves. 📍",
    "Stop doomscrolling. Go do one of these. 📍",
]

OUTRO_LINES = [
    "All ticket links are in the bio 👆",
    "Grab your tickets via the link in bio 👆 (affiliate links — costs you nothing, helps us keep this free)",
    "Links to tickets + full details in bio 👆",
    "Hit the link in bio for tickets and venue info 👆",
]


def _week_number() -> int:
    return datetime.now().isocalendar()[1]


def _format_event_line(event: dict, index: int) -> str:
    name  = event.get("name", "")
    venue = event.get("venue", "")
    date  = event.get("date", "")
    price = event.get("price", "")

    parts = [p for p in [venue, date, price] if p]
    meta  = " · ".join(parts)

    return f"{index:02d}  {name}\n      {meta}"


def _format_opening_line(item: dict) -> str:
    title = item.get("title", "")
    if len(title) > 80:
        title = title[:77] + "…"
    return f"↗  {title}"


def generate_caption(data: dict) -> str:
    """Generate and return the Instagram caption string."""
    events   = data.get("events", [])[:5]
    openings = data.get("openings", [])[:2]

    week_num = _week_number()
    hook     = HOOKS[week_num % len(HOOKS)]
    outro    = OUTRO_LINES[week_num % len(OUTRO_LINES)]

    lines = [hook, ""]

    for i, event in enumerate(events):
        lines.append(_format_event_line(event, i + 1))
        lines.append("")

    if openings:
        lines.append("— New in Aberdeen —")
        for item in openings:
            lines.append(_format_opening_line(item))
        lines.append("")

    lines.append(outro)
    lines.append("")

    # Hashtags pushed below fold with dots (standard Instagram practice)
    lines.append(".")
    lines.append(".")
    lines.append(".")
    lines.append(" ".join(HASHTAGS))

    caption = "\n".join(lines)

    # Save to output/
    output_dir = Path("output/carousels")
    output_dir.mkdir(parents=True, exist_ok=True)
    week_of = data.get("week_of", datetime.now().strftime("%Y-%m-%d"))
    caption_path = output_dir / f"caption-{week_of}.txt"

    with open(caption_path, "w", encoding="utf-8") as f:
        f.write(caption)

    print(f"✅ Caption saved to {caption_path}")
    return caption


if __name__ == "__main__":
    with open("data/combined_weekly.json") as f:
        data = json.load(f)

    caption = generate_caption(data)
    print("\n" + "─" * 50)
    print("INSTAGRAM CAPTION — COPY AND PASTE:")
    print("─" * 50)
    print(caption)
    print("─" * 50)
    print(f"\n({len(caption)} chars — Instagram limit is 2,200)")
