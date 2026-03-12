"""
Aberdeen Insider — Hub Page Generator
Generates docs/index.html — a permanent landing page that never changes URL.
This is the link you put in your Instagram bio, forever.

The page shows:
  - Aberdeen (live this week) → links to latest linkinbio-YYYY-MM-DD.html
  - Coming-soon cities (Glasgow, Edinburgh, Dundee) as teaser rows
  - Newsletter CTA

Output: docs/index.html  (served by GitHub Pages at the permanent URL)
"""

import json
import sys
from datetime import datetime
from pathlib import Path

# Import GA_TRACKING_ID from config if available
try:
    sys.path.insert(0, str(Path(__file__).parent.parent))
    from config import GA_TRACKING_ID
except ImportError:
    GA_TRACKING_ID = ""


# ── Coming-soon cities ────────────────────────────────────────────────────────
COMING_SOON_CITIES = [
    {"number": "02", "name": "Glasgow"},
    {"number": "03", "name": "Edinburgh"},
    {"number": "04", "name": "Dundee"},
]


def _ga4_snippet(tracking_id: str) -> str:
    """Return the GA4 script tags if a tracking ID is configured."""
    if not tracking_id:
        return ""
    return f"""
    <!-- Google Analytics 4 -->
    <script async src="https://www.googletagmanager.com/gtag/js?id={tracking_id}"></script>
    <script>
        window.dataLayer = window.dataLayer || [];
        function gtag(){{dataLayer.push(arguments);}}
        gtag('js', new Date());
        gtag('config', '{tracking_id}');
    </script>"""


def _coming_soon_row(city: dict) -> str:
    return f"""
    <a class="city-row" href="#">
        <div class="city-row-left">
            <span class="city-row-num">{city["number"]} · COMING SOON</span>
            <span class="city-row-name">{city["name"].upper()}</span>
        </div>
        <span class="city-row-arrow">→</span>
    </a>"""


def generate_hub(data: dict) -> str:
    """Generate docs/index.html and return the output path."""

    week_of     = data.get("week_of", datetime.now().strftime("%Y-%m-%d"))
    events      = data.get("events", [])
    event_count = len(events)

    # Human-readable date strings
    try:
        dt           = datetime.strptime(week_of, "%Y-%m-%d")
        date_display = dt.strftime("%-d %b %Y").upper()          # e.g. "12 MAR 2026"
        week_label   = f"WK {dt.isocalendar()[1]} · {dt.strftime('%b %Y').upper()}"
    except ValueError:
        date_display = week_of.upper()
        week_label   = week_of.upper()

    # Path to this week's link-in-bio page (relative URL on GitHub Pages)
    linkinbio_url = f"linkinbio-{week_of}.html"

    coming_soon_html = "".join(_coming_soon_row(c) for c in COMING_SOON_CITIES)
    ga4_html         = _ga4_snippet(GA_TRACKING_ID)

    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Aberdeen Insider — Your City. This Week.</title>
    <meta name="description" content="Aberdeen events, new openings and local tips — every Friday. No filler.">
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Syne:wght@400;700;800&family=DM+Mono:ital,wght@0,400;0,500;1,400&display=swap" rel="stylesheet">{ga4_html}
    <style>
        *, *::before, *::after {{ box-sizing: border-box; margin: 0; padding: 0; }}

        :root {{
            --pitch:     #0A0A0A;
            --parchment: #F5F0E8;
            --strike:    #FFE500;
            --northsea:  #00C4CC;
            --granite:   #8C8C8C;
            --mist:      #EDE9E1;
        }}

        html {{
            background: #1a1a1a;
        }}

        body {{
            font-family: 'DM Mono', monospace;
            background: var(--parchment);
            color: var(--pitch);
            max-width: 480px;
            margin: 0 auto;
            min-height: 100vh;
        }}

        a {{ text-decoration: none; color: inherit; }}

        /* ── Header ────────────────────────────────────────── */
        .header {{
            background: var(--pitch);
            padding: 0 0 0 0;
        }}
        .header-accent {{
            background: var(--strike);
            height: 5px;
        }}
        .header-inner {{
            padding: 24px 28px 22px;
        }}
        .header-eyebrow {{
            font-size: 11px;
            font-weight: 500;
            color: var(--strike);
            letter-spacing: 0.16em;
            text-transform: uppercase;
            margin-bottom: 6px;
        }}
        .header-title {{
            font-family: 'Syne', sans-serif;
            font-size: 36px;
            font-weight: 800;
            color: var(--parchment);
            text-transform: uppercase;
            line-height: 0.95;
            letter-spacing: -0.02em;
        }}
        .header-week {{
            font-size: 11px;
            color: var(--granite);
            letter-spacing: 0.1em;
            margin-top: 10px;
        }}

        /* ── Aberdeen Hero Card ────────────────────────────── */
        .aberdeen-card {{
            background: var(--strike);
            border: 4px solid var(--pitch);
            margin: 20px 20px 0;
            padding: 22px 24px 24px;
            display: flex;
            justify-content: space-between;
            align-items: stretch;
            gap: 16px;
            overflow: hidden;
        }}
        .aberdeen-left {{
            display: flex;
            flex-direction: column;
            justify-content: space-between;
            min-width: 0;
            overflow: hidden;
        }}
        .aberdeen-badge {{
            display: inline-flex;
            align-items: center;
            gap: 6px;
            font-size: 11px;
            font-weight: 500;
            letter-spacing: 0.1em;
            text-transform: uppercase;
            color: var(--pitch);
            background: var(--pitch);
            color: var(--strike);
            padding: 4px 10px;
            align-self: flex-start;
            margin-bottom: 10px;
        }}
        .aberdeen-badge::before {{
            content: '●';
            font-size: 8px;
        }}
        .aberdeen-city {{
            font-family: 'Syne', sans-serif;
            font-size: clamp(28px, 9vw, 46px);
            font-weight: 800;
            text-transform: uppercase;
            line-height: 0.88;
            letter-spacing: -0.03em;
            color: var(--pitch);
            white-space: nowrap;
            overflow: hidden;
            text-overflow: clip;
        }}
        .aberdeen-meta {{
            font-size: 11px;
            font-weight: 500;
            letter-spacing: 0.08em;
            color: var(--pitch);
            margin-top: 12px;
            line-height: 1.7;
            opacity: 0.7;
            white-space: nowrap;
        }}
        .aberdeen-right {{
            display: flex;
            flex-direction: column;
            justify-content: space-between;
            align-items: flex-end;
            flex-shrink: 0;
            min-width: 80px;
        }}
        .aberdeen-categories {{
            display: flex;
            flex-direction: column;
            align-items: flex-end;
            gap: 3px;
            font-size: 11px;
            font-weight: 500;
            letter-spacing: 0.08em;
            text-transform: uppercase;
            color: var(--pitch);
            opacity: 0.65;
            margin-bottom: 16px;
        }}
        .aberdeen-cta {{
            font-family: 'Syne', sans-serif;
            font-size: 14px;
            font-weight: 800;
            text-transform: uppercase;
            letter-spacing: 0.04em;
            color: var(--pitch);
            border-bottom: 2px solid var(--pitch);
            padding-bottom: 2px;
            white-space: nowrap;
        }}

        /* ── Coming-Soon City Rows ─────────────────────────── */
        .cities-stack {{
            margin: 0 20px;
            border-left: 4px solid var(--pitch);
            border-right: 4px solid var(--pitch);
        }}
        .city-row {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            background: var(--mist);
            border-bottom: 2px dashed var(--pitch);
            padding: 16px 20px;
            cursor: default;
        }}
        .city-row:last-child {{
            border-bottom: none;
        }}
        .city-row-left {{
            display: flex;
            flex-direction: column;
            gap: 2px;
        }}
        .city-row-num {{
            font-size: 10px;
            font-weight: 500;
            letter-spacing: 0.12em;
            color: var(--granite);
            text-transform: uppercase;
        }}
        .city-row-name {{
            font-family: 'Syne', sans-serif;
            font-size: 28px;
            font-weight: 800;
            text-transform: uppercase;
            letter-spacing: -0.02em;
            line-height: 1;
            white-space: nowrap;
        }}
        .city-row-arrow {{
            font-size: 22px;
            color: var(--granite);
        }}

        /* ── Newsletter CTA ────────────────────────────────── */
        .newsletter-cta {{
            background: var(--pitch);
            margin: 20px 20px 0;
            padding: 24px;
            border: 3px solid var(--strike);
        }}
        .cta-label {{
            font-size: 11px;
            font-weight: 500;
            color: var(--strike);
            letter-spacing: 0.14em;
            text-transform: uppercase;
            margin-bottom: 8px;
        }}
        .cta-headline {{
            font-family: 'Syne', sans-serif;
            font-size: 22px;
            font-weight: 800;
            color: var(--parchment);
            text-transform: uppercase;
            line-height: 1.1;
            margin-bottom: 8px;
        }}
        .cta-body {{
            font-size: 13px;
            color: var(--granite);
            line-height: 1.7;
            margin-bottom: 18px;
        }}
        .cta-btn {{
            display: block;
            text-align: center;
            background: var(--strike);
            color: var(--pitch);
            font-family: 'DM Mono', monospace;
            font-size: 14px;
            font-weight: 500;
            letter-spacing: 0.06em;
            text-transform: uppercase;
            text-decoration: none;
            padding: 14px 20px;
        }}

        /* ── Footer ────────────────────────────────────────── */
        .footer {{
            border-top: 3px solid var(--pitch);
            margin: 20px 20px 0;
            padding: 16px 0 24px;
            display: flex;
            justify-content: space-between;
            align-items: center;
            flex-wrap: wrap;
            gap: 8px;
        }}
        .footer-updated {{
            font-size: 11px;
            font-weight: 500;
            letter-spacing: 0.1em;
            text-transform: uppercase;
            color: var(--granite);
        }}
        .footer-cta {{
            font-size: 11px;
            font-weight: 500;
            letter-spacing: 0.08em;
            text-transform: uppercase;
            color: var(--pitch);
            border-bottom: 1px solid var(--pitch);
        }}
    </style>
</head>
<body>

    <!-- ── Header ──────────────────────────────────────────── -->
    <header class="header">
        <div class="header-accent"></div>
        <div class="header-inner">
            <div class="header-eyebrow">Insider</div>
            <div class="header-title">Your City.<br>This Week.</div>
            <div class="header-week">{week_label}</div>
        </div>
    </header>

    <!-- ── Aberdeen Hero ────────────────────────────────────── -->
    <a href="{linkinbio_url}" class="aberdeen-card">
        <div class="aberdeen-left">
            <div>
                <div class="aberdeen-badge">Live This Week</div>
                <div class="aberdeen-city">Aberdeen</div>
            </div>
            <div class="aberdeen-meta">
                {event_count} EVENTS · SCOTLAND<br>
                FRI {date_display}
            </div>
        </div>
        <div class="aberdeen-right">
            <div class="aberdeen-categories">
                <span>Nights Out</span>
                <span>Food</span>
                <span>Events</span>
                <span>New In</span>
            </div>
            <div class="aberdeen-cta">View All →</div>
        </div>
    </a>

    <!-- ── Coming-Soon Cities ───────────────────────────────── -->
    <div class="cities-stack">
        {coming_soon_html}
    </div>

    <!-- ── Newsletter CTA ───────────────────────────────────── -->
    <div class="newsletter-cta">
        <div class="cta-label">Never Miss a Drop</div>
        <div class="cta-headline">Get it in<br>your inbox.</div>
        <p class="cta-body">Free weekly newsletter. Aberdeen events, new openings, local tips. Under 3 minutes to read.</p>
        <a href="#" class="cta-btn">Subscribe Free →</a>
    </div>

    <!-- ── Footer ──────────────────────────────────────────── -->
    <footer class="footer">
        <span class="footer-updated">Updated every Friday</span>
        <a href="mailto:hello@abdn.insider" class="footer-cta">Want your city? Get in touch →</a>
    </footer>

</body>
</html>"""

    # Save to docs/ — this is what GitHub Pages serves
    docs_dir = Path("docs")
    docs_dir.mkdir(exist_ok=True)
    output_path = docs_dir / "index.html"
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(html)

    print(f"✅ Hub page saved to {output_path}")
    print(f"   → Links to: {linkinbio_url}")
    return str(output_path)


if __name__ == "__main__":
    # Allow running standalone with real data or dummy data
    data_path = Path("data/combined_weekly.json")
    if data_path.exists():
        with open(data_path) as f:
            data = json.load(f)
    else:
        # Dummy data for testing
        data = {
            "week_of": datetime.now().strftime("%Y-%m-%d"),
            "events": [{}] * 9,   # 9 placeholder events
            "openings": [],
            "news": [],
        }
    generate_hub(data)
