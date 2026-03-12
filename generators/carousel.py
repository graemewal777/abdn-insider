"""
Aberdeen Insider — Carousel Generator
Generates 1080×1080px HTML slides and screenshots them to PNG.

Slide structure (matches Paper designs):
  01 — Cover        black bg, "THIS WEEKEND." yellow accents
  02–06 — Events    parchment bg, up to 5 events
  07+ — Opening     teal bg, new venue/opening
  Last — CTA        yellow bg, "FOLLOW FOR WEEKLY DROPS."

Output: output/carousels/week-YYYY-MM-DD/
  slide-01-cover.html / .png
  slide-02-event.html / .png  (etc.)
  slide-07-cta.html / .png
"""

import json
from datetime import datetime, timedelta
from pathlib import Path

try:
    from config import HASHTAGS, INSTAGRAM_HANDLE
except ImportError:
    HASHTAGS = [
        "#aberdeen", "#aberdeenscotland", "#aberdeenevents",
        "#thingstodoaberdeen", "#aberdeenlife", "#weekendinaberdeen",
        "#abdn", "#aberdeenfood", "#aberdeennightlife", "#visitaberdeen",
    ]
    INSTAGRAM_HANDLE = "@abdn.insider"

GOOGLE_FONTS = (
    "https://fonts.googleapis.com/css2?"
    "family=Syne:wght@400;700;800"
    "&family=DM+Mono:ital,wght@0,400;0,500;1,400"
    "&display=swap"
)


# ── Helpers ────────────────────────────────────────────────────────────────────

def _wrap(body: str, bg: str = "#F5F0E8") -> str:
    """Wrap slide body in a full 1080×1080 HTML document."""
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=1080">
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="{GOOGLE_FONTS}" rel="stylesheet">
  <style>
    *, *::before, *::after {{ box-sizing: border-box; margin: 0; padding: 0; }}
    html, body {{
      width: 1080px; height: 1080px;
      overflow: hidden;
      background: {bg};
      -webkit-font-smoothing: antialiased;
      font-synthesis: none;
    }}
  </style>
</head>
<body>
{body}
</body>
</html>"""


def _event_name_size(name: str) -> int:
    """Pick font size so the event name fits without overflow."""
    n = len(name)
    if n <= 18:  return 96
    if n <= 28:  return 80
    if n <= 40:  return 68
    if n <= 55:  return 54
    return 44


# ── Slide generators ───────────────────────────────────────────────────────────

def _cover_html(events: list, openings: list, date_from: str, date_to: str) -> str:
    n_e = len(events)
    n_o = len(openings)
    parts = []
    if n_e:
        parts.append(f"{n_e} event{'s' if n_e != 1 else ''}")
    if n_o:
        parts.append(f"{n_o} new opening{'s' if n_o != 1 else ''}")
    summary = ". ".join(parts) + ". All worth your time." if parts else "All worth your time."

    body = f"""
<div style="
  width:1080px; height:1080px;
  background:#0A0A0A;
  border:4px solid #0A0A0A;
  padding:64px;
  display:flex; flex-direction:column;
">
  <!-- Top bar -->
  <div style="display:flex; justify-content:space-between; align-items:flex-end; flex-shrink:0;">
    <div style="font-family:'DM Mono',monospace; font-size:14px; letter-spacing:0.08em; color:#8C8C8C; text-transform:uppercase;">{INSTAGRAM_HANDLE}</div>
    <div style="font-family:'DM Mono',monospace; font-size:14px; letter-spacing:0.06em; color:#8C8C8C;">{date_from} – {date_to}</div>
  </div>

  <!-- Yellow rule -->
  <div style="height:3px; background:#FFE500; margin-top:20px; flex-shrink:0;"></div>

  <!-- THIS WEEKEND -->
  <div style="
    font-family:'Syne',sans-serif; font-weight:800;
    font-size:168px; line-height:0.88;
    letter-spacing:-0.03em;
    color:#F5F0E8; text-transform:uppercase;
    margin-top:36px; flex-grow:1;
  ">THIS<br>WEEK<br>END.</div>

  <!-- Bottom -->
  <div style="flex-shrink:0;">
    <div style="display:flex; justify-content:space-between; align-items:flex-end; margin-bottom:20px;">
      <div>
        <div style="font-family:'DM Mono',monospace; font-size:15px; color:#8C8C8C; line-height:1.5;">{summary}</div>
        <div style="font-family:'Syne',sans-serif; font-weight:800; font-size:28px; color:#FFE500; text-transform:uppercase; letter-spacing:-0.01em; margin-top:8px;">ABERDEEN</div>
      </div>
      <div style="font-family:'DM Mono',monospace; font-size:14px; color:#8C8C8C; text-align:right; line-height:1.5;">Swipe for this<br>week's picks ›</div>
    </div>
    <div style="height:3px; background:#FFE500;"></div>
  </div>
</div>"""
    return _wrap(body, "#0A0A0A")


def _event_html(event: dict, index: int, total: int) -> str:
    name     = event.get("name", "Untitled").upper()
    venue    = event.get("venue", "TBC")
    date     = event.get("date", "")
    time     = event.get("time", "TBC") or "TBC"
    price    = event.get("price", "")
    category = event.get("category", "Event").upper()
    vibe     = event.get("vibe_note", "")
    fs       = _event_name_size(name)

    # Price pill styling
    if price == "Free":
        price_html = '<div style="background:#0A0A0A; padding:2px 10px; display:inline-block;"><span style="font-family:\'Syne\',sans-serif; font-size:22px; font-weight:800; color:#FFE500;">Free</span></div>'
    elif price:
        price_html = f'<div style="background:#FFE500; padding:2px 10px; display:inline-block;"><span style="font-family:\'Syne\',sans-serif; font-size:22px; font-weight:800; color:#0A0A0A;">{price}</span></div>'
    else:
        price_html = '<div style="font-family:\'Syne\',sans-serif; font-size:22px; font-weight:700; color:#8C8C8C;">TBC</div>'

    vibe_html = ""
    if vibe:
        vibe_html = f"""
    <div style="border-left:4px solid #FFE500; padding-left:16px; margin-top:20px;">
      <div style="font-family:'DM Mono',monospace; font-size:17px; font-style:italic; line-height:1.6; color:#0A0A0A;">{vibe}</div>
    </div>"""

    body = f"""
<div style="
  width:1080px; height:1080px;
  background:#F5F0E8;
  border:4px solid #0A0A0A;
  padding:64px;
  display:flex; flex-direction:column;
">
  <!-- Header: ghost number + category/date -->
  <div style="display:flex; justify-content:space-between; align-items:flex-start; flex-shrink:0;">
    <div style="font-family:'Syne',sans-serif; font-weight:800; font-size:160px; line-height:1; letter-spacing:-0.04em; color:#0A0A0A; opacity:0.12;">{index:02d}</div>
    <div style="display:flex; flex-direction:column; align-items:flex-end; gap:8px; padding-top:12px;">
      <div style="background:#0A0A0A; padding:5px 14px;">
        <span style="font-family:'DM Mono',monospace; font-size:13px; font-weight:500; letter-spacing:0.1em; text-transform:uppercase; color:#F5F0E8;">{category}</span>
      </div>
      <div style="font-family:'DM Mono',monospace; font-size:13px; letter-spacing:0.06em; color:#8C8C8C;">{date}</div>
    </div>
  </div>

  <!-- Rule -->
  <div style="height:3px; background:#0A0A0A; margin-top:8px; flex-shrink:0;"></div>

  <!-- Event name -->
  <div style="
    font-family:'Syne',sans-serif; font-weight:800;
    font-size:{fs}px; line-height:0.92;
    letter-spacing:-0.02em; text-transform:uppercase; color:#0A0A0A;
    margin-top:32px; flex-grow:1; overflow:hidden;
  ">{name}</div>

  <!-- Footer section -->
  <div style="flex-shrink:0; margin-top:auto;">
    <!-- VENUE / DOORS / TICKETS -->
    <div style="display:flex; border-top:3px solid #0A0A0A; padding-top:24px;">
      <div style="flex:1; border-right:3px solid #0A0A0A; padding-right:28px; display:flex; flex-direction:column; gap:6px;">
        <div style="font-family:'DM Mono',monospace; font-size:14px; letter-spacing:0.1em; text-transform:uppercase; color:#8C8C8C;">Venue</div>
        <div style="font-family:'Syne',sans-serif; font-size:24px; font-weight:700; color:#0A0A0A; line-height:1.1;">{venue}</div>
      </div>
      <div style="flex:1; border-right:3px solid #0A0A0A; padding-inline:28px; display:flex; flex-direction:column; gap:6px;">
        <div style="font-family:'DM Mono',monospace; font-size:14px; letter-spacing:0.1em; text-transform:uppercase; color:#8C8C8C;">Doors</div>
        <div style="font-family:'Syne',sans-serif; font-size:24px; font-weight:700; color:#0A0A0A; line-height:1.1;">{time}</div>
      </div>
      <div style="padding-left:28px; display:flex; flex-direction:column; gap:6px;">
        <div style="font-family:'DM Mono',monospace; font-size:14px; letter-spacing:0.1em; text-transform:uppercase; color:#8C8C8C;">Tickets</div>
        {price_html}
      </div>
    </div>

    {vibe_html}

    <!-- Footer bar -->
    <div style="display:flex; justify-content:space-between; align-items:center; border-top:2px solid #0A0A0A; margin-top:28px; padding-top:16px;">
      <div style="font-family:'DM Mono',monospace; font-size:15px; letter-spacing:0.08em; color:#8C8C8C;">{INSTAGRAM_HANDLE}</div>
      <div style="font-family:'DM Mono',monospace; font-size:15px; color:#8C8C8C;">{index + 1} / {total}</div>
    </div>
  </div>
</div>"""
    return _wrap(body, "#F5F0E8")


def _opening_html(opening: dict, slide_num: int, total: int) -> str:
    title   = opening.get("title", "New Opening").upper()
    summary = opening.get("summary", "")[:220]
    fs      = _event_name_size(title)

    body = f"""
<div style="
  width:1080px; height:1080px;
  background:#00C4CC;
  border:4px solid #0A0A0A;
  padding:64px;
  display:flex; flex-direction:column;
">
  <!-- Tag -->
  <div style="flex-shrink:0;">
    <div style="display:inline-block; background:#0A0A0A; padding:5px 14px;">
      <span style="font-family:'DM Mono',monospace; font-size:13px; font-weight:500; letter-spacing:0.12em; text-transform:uppercase; color:#00C4CC;">New Opening ✦</span>
    </div>
  </div>

  <!-- Rule -->
  <div style="height:3px; background:#0A0A0A; margin-top:24px; flex-shrink:0;"></div>

  <!-- Title -->
  <div style="
    font-family:'Syne',sans-serif; font-weight:800;
    font-size:{fs}px; line-height:0.92;
    letter-spacing:-0.02em; text-transform:uppercase; color:#0A0A0A;
    margin-top:36px; flex-grow:1; overflow:hidden;
  ">{title}</div>

  <!-- Summary + footer -->
  <div style="flex-shrink:0;">
    <div style="border-left:4px solid #0A0A0A; padding-left:16px; margin-bottom:28px;">
      <div style="font-family:'DM Mono',monospace; font-size:15px; line-height:1.6; color:#0A0A0A;">{summary}</div>
    </div>
    <div style="height:2px; background:#0A0A0A; margin-bottom:16px;"></div>
    <div style="display:flex; justify-content:space-between; align-items:center;">
      <div style="font-family:'DM Mono',monospace; font-size:15px; letter-spacing:0.08em; color:#0A0A0A; opacity:0.6;">{INSTAGRAM_HANDLE}</div>
      <div style="font-family:'DM Mono',monospace; font-size:15px; color:#0A0A0A; opacity:0.6;">{slide_num} / {total}</div>
    </div>
  </div>
</div>"""
    return _wrap(body, "#00C4CC")


def _cta_html(total: int) -> str:
    hashtag_str = "  ".join(HASHTAGS)

    body = f"""
<div style="
  width:1080px; height:1080px;
  background:#FFE500;
  border:4px solid #0A0A0A;
  padding:64px;
  display:flex; flex-direction:column;
">
  <!-- Top rule -->
  <div style="height:3px; background:#0A0A0A; flex-shrink:0;"></div>

  <!-- BIG TEXT -->
  <div style="
    font-family:'Syne',sans-serif; font-weight:800;
    font-size:130px; line-height:0.88;
    letter-spacing:-0.03em; text-transform:uppercase; color:#0A0A0A;
    margin-top:44px; flex-grow:1; overflow:hidden;
  ">FOLLOW<br>FOR<br>WEEKLY<br>DROPS.</div>

  <!-- Mid rule -->
  <div style="height:3px; background:#0A0A0A; margin-bottom:28px; flex-shrink:0;"></div>

  <!-- Handle + copy -->
  <div style="display:flex; justify-content:space-between; align-items:flex-end; margin-bottom:36px; flex-shrink:0;">
    <div style="font-family:'DM Mono',monospace; font-size:22px; font-weight:500; letter-spacing:0.06em; text-transform:uppercase; color:#0A0A0A;">{INSTAGRAM_HANDLE.upper()}</div>
    <div style="font-family:'DM Mono',monospace; font-size:13px; color:#0A0A0A; text-align:right; line-height:1.55; max-width:320px;">Every Friday. Aberdeen events, new<br>openings, local tips. No algorithm. No<br>filler. Just the good stuff.</div>
  </div>

  <!-- Hashtags -->
  <div style="font-family:'DM Mono',monospace; font-size:11px; color:#0A0A0A; opacity:0.45; line-height:1.8; margin-bottom:24px; flex-shrink:0;">{hashtag_str}</div>

  <!-- Bottom rule + slide count -->
  <div style="flex-shrink:0;">
    <div style="height:3px; background:#0A0A0A;"></div>
    <div style="font-family:'DM Mono',monospace; font-size:12px; color:#0A0A0A; text-align:right; margin-top:14px; opacity:0.5;">{total} / {total}</div>
  </div>
</div>"""
    return _wrap(body, "#FFE500")


# ── Screenshot ─────────────────────────────────────────────────────────────────

def _screenshot_slides(slide_dir: Path) -> list:
    """Screenshot every HTML slide in slide_dir to a PNG at 1080×1080."""
    from playwright.sync_api import sync_playwright

    html_files = sorted(slide_dir.glob("*.html"))
    png_files  = []

    with sync_playwright() as p:
        browser = p.chromium.launch()
        page    = browser.new_page(viewport={"width": 1080, "height": 1080})

        for html_file in html_files:
            png_path = html_file.with_suffix(".png")
            page.goto(f"file://{html_file.resolve()}", wait_until="networkidle")
            page.screenshot(
                path=str(png_path),
                clip={"x": 0, "y": 0, "width": 1080, "height": 1080},
            )
            png_files.append(png_path)
            print(f"   📸 {html_file.name}")

        browser.close()

    return png_files


# ── Main entry ─────────────────────────────────────────────────────────────────

def generate_carousel(data: dict) -> str:
    """Generate carousel slides and screenshot to PNG. Returns output directory path."""

    week_of  = data.get("week_of", datetime.now().strftime("%Y-%m-%d"))
    events   = data.get("events", [])[:5]     # cap at 5 event slides
    openings = data.get("openings", [])[:2]   # cap at 2 opening slides

    # Weekend date range for cover slide
    try:
        week_dt     = datetime.strptime(week_of, "%Y-%m-%d")
        days_to_fri = (4 - week_dt.weekday()) % 7
        friday      = week_dt + timedelta(days=days_to_fri)
        sunday      = friday + timedelta(days=2)
        date_from   = friday.strftime("%-d %b %Y")
        date_to     = sunday.strftime("%-d %b %Y")
    except (ValueError, AttributeError):
        date_from = date_to = week_of

    total      = 1 + len(events) + len(openings) + 1  # cover + events + openings + CTA
    output_dir = Path("output/carousels") / f"week-{week_of}"
    output_dir.mkdir(parents=True, exist_ok=True)

    slide_num = 0

    # Slide 1 — Cover
    slide_num += 1
    (output_dir / f"slide-{slide_num:02d}-cover.html").write_text(
        _cover_html(events, openings, date_from, date_to), encoding="utf-8"
    )

    # Event slides
    for i, event in enumerate(events):
        slide_num += 1
        (output_dir / f"slide-{slide_num:02d}-event.html").write_text(
            _event_html(event, i + 1, total), encoding="utf-8"
        )

    # Opening slides
    for opening in openings:
        slide_num += 1
        (output_dir / f"slide-{slide_num:02d}-opening.html").write_text(
            _opening_html(opening, slide_num, total), encoding="utf-8"
        )

    # CTA slide
    slide_num += 1
    (output_dir / f"slide-{slide_num:02d}-cta.html").write_text(
        _cta_html(total), encoding="utf-8"
    )

    print(f"\n✅ {slide_num} slides generated → {output_dir}")

    # Screenshot to PNG
    try:
        pngs = _screenshot_slides(output_dir)
        print(f"✅ {len(pngs)} PNGs ready to upload to Instagram")
    except ImportError:
        print("⚠️  playwright not installed — HTML slides only. To enable PNG screenshots:")
        print("   pip3 install playwright && playwright install chromium")

    return str(output_dir)


if __name__ == "__main__":
    with open("data/combined_weekly.json") as f:
        data = json.load(f)
    generate_carousel(data)
