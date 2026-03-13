"""
Aberdeen Insider — Hub Page Generator
Generates docs/index.html — permanent landing page, desktop-first design.
Bio link that never changes URL.

Output: docs/index.html (served by GitHub Pages)
"""

import json
import sys
from datetime import datetime
from pathlib import Path

try:
    sys.path.insert(0, str(Path(__file__).parent.parent))
    from config import GA_TRACKING_ID
except ImportError:
    GA_TRACKING_ID = ""

COMING_SOON_CITIES = [
    {"number": "02", "name": "Glasgow"},
    {"number": "03", "name": "Edinburgh"},
    {"number": "04", "name": "Dundee"},
]


def _ga4_snippet(tracking_id: str) -> str:
    if not tracking_id:
        return ""
    return f"""
    <script async src="https://www.googletagmanager.com/gtag/js?id={tracking_id}"></script>
    <script>
        window.dataLayer = window.dataLayer || [];
        function gtag(){{dataLayer.push(arguments);}}
        gtag('js', new Date());
        gtag('config', '{tracking_id}');
    </script>"""


def _city_row(city: dict) -> str:
    return f"""
          <div class="city-row">
            <div class="city-row-left">
              <span class="city-num">{city["number"]}</span>
              <span class="city-pill">Coming Soon</span>
              <span class="city-name">{city["name"].upper()}</span>
            </div>
            <span class="city-arrow">→</span>
          </div>"""


def generate_hub(data: dict) -> str:
    week_of     = data.get("week_of", datetime.now().strftime("%Y-%m-%d"))
    events      = data.get("events", [])
    event_count = len(events)

    try:
        dt           = datetime.strptime(week_of, "%Y-%m-%d")
        date_display = dt.strftime("%-d %b %Y").upper()
        week_label   = f"WK {dt.isocalendar()[1]} · {dt.strftime('%b %Y').upper()}"
    except ValueError:
        date_display = week_of.upper()
        week_label   = week_of.upper()

    linkinbio_url    = f"linkinbio-{week_of}.html"
    cities_html      = "".join(_city_row(c) for c in COMING_SOON_CITIES)
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
  <link href="https://fonts.googleapis.com/css2?family=Syne:wght@800&family=DM+Mono:wght@400;500&display=swap" rel="stylesheet">{ga4_html}
  <style>
    *, *::before, *::after {{ box-sizing: border-box; margin: 0; padding: 0; }}

    :root {{
      --pitch:     #0A0A0A;
      --parchment: #F5F0E8;
      --strike:    #FFE500;
      --granite:   #8C8C8C;
      --mist:      #EDE9E1;
    }}

    html {{
      background: var(--pitch);
      min-height: 100%;
    }}

    body {{
      font-family: 'DM Mono', monospace;
      background: var(--pitch);
      color: var(--pitch);
      display: flex;
      justify-content: center;
      min-height: 100vh;
    }}

    a {{ text-decoration: none; color: inherit; display: block; }}

    /* ── Page shell ─────────────────────────────────────────── */
    .page {{
      width: 100%;
      max-width: 1200px;
      background: var(--parchment);
      border-left: 3px solid var(--pitch);
      border-right: 3px solid var(--pitch);
      display: flex;
      flex-direction: column;
    }}

    /* ── Header ─────────────────────────────────────────────── */
    .header {{
      background: var(--pitch);
    }}
    .header-stripe {{
      height: 6px;
      background: var(--strike);
    }}
    .header-inner {{
      display: flex;
      align-items: flex-end;
      justify-content: space-between;
      padding: 32px 48px 28px;
      gap: 24px;
    }}
    .header-eyebrow {{
      font-size: 11px;
      font-weight: 500;
      color: var(--strike);
      letter-spacing: 0.18em;
      text-transform: uppercase;
      margin-bottom: 8px;
    }}
    .header-title {{
      font-family: 'Syne', sans-serif;
      font-size: 64px;
      font-weight: 800;
      color: var(--parchment);
      text-transform: uppercase;
      line-height: 0.9;
      letter-spacing: -0.03em;
    }}
    .header-week {{
      font-size: 12px;
      color: var(--granite);
      letter-spacing: 0.12em;
      text-transform: uppercase;
      white-space: nowrap;
      padding-bottom: 8px;
    }}

    /* ── Aberdeen Hero ──────────────────────────────────────── */
    .hero {{
      background: var(--strike);
      border-bottom: 3px solid var(--pitch);
      padding: 40px 48px;
      display: flex;
      flex-direction: column;
      gap: 20px;
      overflow: hidden;
    }}
    .hero-top {{
      display: flex;
      align-items: center;
      justify-content: space-between;
      gap: 24px;
    }}
    .hero-badge {{
      display: inline-flex;
      align-items: center;
      gap: 8px;
      background: var(--pitch);
      color: var(--strike);
      font-size: 11px;
      font-weight: 500;
      letter-spacing: 0.14em;
      text-transform: uppercase;
      padding: 6px 14px;
      white-space: nowrap;
    }}
    .hero-tags {{
      display: flex;
      gap: 8px;
    }}
    .hero-tag {{
      font-size: 11px;
      font-weight: 500;
      letter-spacing: 0.12em;
      text-transform: uppercase;
      color: var(--pitch);
      border: 2px solid rgba(10,10,10,0.4);
      padding: 4px 12px;
    }}
    .hero-city {{
      font-family: 'Syne', sans-serif;
      font-size: 96px;
      font-weight: 800;
      text-transform: uppercase;
      line-height: 0.85;
      letter-spacing: -0.03em;
      color: var(--pitch);
    }}
    .hero-bottom {{
      display: flex;
      align-items: flex-end;
      justify-content: space-between;
      gap: 24px;
      border-top: 2px solid rgba(10,10,10,0.18);
      padding-top: 18px;
    }}
    .hero-meta {{
      font-size: 13px;
      font-weight: 500;
      letter-spacing: 0.08em;
      text-transform: uppercase;
      color: var(--pitch);
      opacity: 0.6;
      line-height: 1.8;
    }}
    .hero-cta {{
      font-family: 'Syne', sans-serif;
      font-size: 20px;
      font-weight: 800;
      text-transform: uppercase;
      letter-spacing: 0.01em;
      color: var(--pitch);
      border-bottom: 3px solid var(--pitch);
      padding-bottom: 3px;
      white-space: nowrap;
    }}

    /* ── City Rows ──────────────────────────────────────────── */
    .cities {{
      border-bottom: 3px solid var(--pitch);
    }}
    .city-row {{
      display: flex;
      align-items: center;
      justify-content: space-between;
      padding: 22px 48px;
      background: var(--mist);
      border-bottom: 2px dashed var(--pitch);
    }}
    .city-row:last-child {{
      border-bottom: none;
    }}
    .city-row-left {{
      display: flex;
      align-items: center;
      gap: 20px;
    }}
    .city-num {{
      font-size: 11px;
      font-weight: 500;
      letter-spacing: 0.14em;
      color: var(--granite);
      text-transform: uppercase;
    }}
    .city-pill {{
      font-size: 11px;
      font-weight: 500;
      letter-spacing: 0.12em;
      text-transform: uppercase;
      color: var(--granite);
      border: 1px solid var(--granite);
      padding: 2px 10px;
      white-space: nowrap;
    }}
    .city-name {{
      font-family: 'Syne', sans-serif;
      font-size: 48px;
      font-weight: 800;
      text-transform: uppercase;
      letter-spacing: -0.03em;
      line-height: 1;
      color: var(--pitch);
    }}
    .city-arrow {{
      font-size: 24px;
      color: var(--granite);
    }}

    /* ── Newsletter ─────────────────────────────────────────── */
    .newsletter {{
      background: var(--pitch);
      padding: 48px;
      border-bottom: 3px solid var(--strike);
      display: flex;
      align-items: center;
      justify-content: space-between;
      gap: 48px;
    }}
    .newsletter-left {{
      display: flex;
      flex-direction: column;
      gap: 12px;
    }}
    .newsletter-eyebrow {{
      font-size: 11px;
      font-weight: 500;
      color: var(--strike);
      letter-spacing: 0.16em;
      text-transform: uppercase;
    }}
    .newsletter-headline {{
      font-family: 'Syne', sans-serif;
      font-size: 48px;
      font-weight: 800;
      color: var(--parchment);
      text-transform: uppercase;
      line-height: 0.92;
      letter-spacing: -0.02em;
    }}
    .newsletter-right {{
      display: flex;
      flex-direction: column;
      align-items: flex-end;
      gap: 16px;
      flex-shrink: 0;
      max-width: 320px;
    }}
    .newsletter-body {{
      font-size: 13px;
      color: var(--granite);
      line-height: 1.7;
      text-align: right;
    }}
    .newsletter-btn {{
      display: inline-block;
      background: var(--strike);
      color: var(--pitch);
      font-size: 14px;
      font-weight: 500;
      letter-spacing: 0.08em;
      text-transform: uppercase;
      padding: 16px 36px;
      white-space: nowrap;
    }}

    /* ── Footer ─────────────────────────────────────────────── */
    .footer {{
      padding: 18px 48px;
      display: flex;
      justify-content: space-between;
      align-items: center;
      background: var(--parchment);
    }}
    .footer-label {{
      font-size: 11px;
      font-weight: 500;
      letter-spacing: 0.12em;
      text-transform: uppercase;
      color: var(--granite);
    }}
    .footer-link {{
      font-size: 11px;
      font-weight: 500;
      letter-spacing: 0.1em;
      text-transform: uppercase;
      color: var(--pitch);
      border-bottom: 1px solid var(--pitch);
      display: inline;
    }}
  </style>
</head>
<body>
<div class="page">

  <!-- Header -->
  <header class="header">
    <div class="header-stripe"></div>
    <div class="header-inner">
      <div>
        <div class="header-eyebrow">Insider</div>
        <div class="header-title">Your City.<br>This Week.</div>
      </div>
      <div class="header-week">{week_label}</div>
    </div>
  </header>

  <!-- Aberdeen Hero -->
  <a href="{linkinbio_url}" class="hero">
    <div class="hero-top">
      <div class="hero-badge">● Live This Week</div>
      <div class="hero-tags">
        <span class="hero-tag">Nights Out</span>
        <span class="hero-tag">Food</span>
        <span class="hero-tag">Events</span>
        <span class="hero-tag">New In</span>
      </div>
    </div>
    <div class="hero-city">Aberdeen</div>
    <div class="hero-bottom">
      <div class="hero-meta">
        {event_count} events this weekend<br>
        Updated Fri {date_display} · Scotland
      </div>
      <div class="hero-cta">View All Events →</div>
    </div>
  </a>

  <!-- Coming-Soon Cities -->
  <div class="cities">
    {cities_html}
  </div>

  <!-- Newsletter -->
  <div class="newsletter">
    <div class="newsletter-left">
      <div class="newsletter-eyebrow">Never Miss a Drop</div>
      <div class="newsletter-headline">Get It In<br>Your Inbox.</div>
    </div>
    <div class="newsletter-right">
      <div class="newsletter-body">Free weekly newsletter. Aberdeen events, new openings, local tips. Under 3 minutes to read.</div>
      <a href="https://abdn-insider.beehiiv.com/subscribe" class="newsletter-btn" target="_blank">Subscribe Free →</a>
    </div>
  </div>

  <!-- Footer -->
  <footer class="footer">
    <span class="footer-label">Updated Every Friday</span>
    <a href="mailto:hello@abdn.insider" class="footer-link">Want Your City? Get In Touch →</a>
  </footer>

</div>
</body>
</html>"""

    docs_dir = Path("docs")
    docs_dir.mkdir(exist_ok=True)
    output_path = docs_dir / "index.html"
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(html)

    print(f"✅ Hub page saved to {output_path}")
    print(f"   → Links to: {linkinbio_url}")
    return str(output_path)


if __name__ == "__main__":
    data_path = Path("data/combined_weekly.json")
    if data_path.exists():
        with open(data_path) as f:
            data = json.load(f)
    else:
        data = {
            "week_of": datetime.now().strftime("%Y-%m-%d"),
            "events": [{}] * 12,
            "openings": [],
            "news": [],
        }
    generate_hub(data)
