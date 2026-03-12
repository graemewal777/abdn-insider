"""
Aberdeen Insider — Link-in-Bio Page Generator
Generates a mobile-first HTML page each week with all events + affiliate
ticket links + new openings. Lives at your bio URL, updated every Friday.

Output: output/newsletters/linkinbio-YYYY-MM-DD.html
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


def _ga4_snippet(tracking_id: str) -> str:
    """Return GA4 script tags if a tracking ID is configured."""
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


def _event_card(event: dict, index: int) -> str:
    price = event.get("price", "")
    price_bg = "#FFE500" if price != "Free" else "#0A0A0A"
    price_color = "#0A0A0A" if price != "Free" else "#FFE500"

    ticket_url = event.get("url", "")
    ticket_btn = ""
    if ticket_url:
        label = "Get Tickets" if price != "Free" else "More Info"
        ticket_btn = f"""
        <a href="{ticket_url}" target="_blank" rel="noopener" class="ticket-btn">
            {label} →
        </a>"""

    vibe = event.get("vibe_note", "")
    vibe_html = f'<p class="vibe">{vibe}</p>' if vibe else ""

    return f"""
    <div class="event-card">
        <div class="event-header">
            <span class="event-num">{index:02d}</span>
            <span class="event-category">{event.get("category", "")}</span>
        </div>
        <h3 class="event-name">{event.get("name", "")}</h3>
        <div class="event-meta">
            <span class="meta-item">{event.get("venue", "")}</span>
            <span class="meta-dot">·</span>
            <span class="meta-item">{event.get("date", "")}</span>
            <span class="meta-dot">·</span>
            <span class="meta-item">{event.get("time", "")}</span>
            <span class="price-tag" style="background:{price_bg};color:{price_color};">{price}</span>
        </div>
        {vibe_html}
        {ticket_btn}
    </div>"""


def _opening_card(item: dict) -> str:
    url = item.get("url", "")
    link_html = ""
    if url:
        link_html = f'<a href="{url}" target="_blank" rel="noopener" class="read-more">Read more →</a>'

    return f"""
    <div class="opening-card">
        <span class="opening-source">{item.get("source", "")}</span>
        <h3 class="opening-title">{item.get("title", "")}</h3>
        <p class="opening-summary">{item.get("summary", "")[:200]}{"…" if len(item.get("summary","")) > 200 else ""}</p>
        {link_html}
    </div>"""


def generate_linkinbio(data: dict) -> str:
    """Generate the link-in-bio HTML page and return the output path."""

    week_of = data.get("week_of", datetime.now().strftime("%Y-%m-%d"))
    events   = data.get("events", [])
    openings = data.get("openings", [])

    try:
        date_display = datetime.strptime(week_of, "%Y-%m-%d").strftime("%-d %B %Y")
    except ValueError:
        date_display = week_of

    events_html   = "\n".join(_event_card(e, i + 1) for i, e in enumerate(events))
    openings_html = "\n".join(_opening_card(o) for o in openings) if openings else ""
    ga4_html      = _ga4_snippet(GA_TRACKING_ID)

    openings_section = ""
    if openings_html:
        openings_section = f"""
    <section class="section">
        <div class="section-label teal">New In Aberdeen</div>
        {openings_html}
    </section>"""

    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Aberdeen Insider — Week of {date_display}</title>
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
            --alert:     #FF3B30;
        }}

        /* Dark surround on desktop — looks like a phone frame */
        html {{
            background: #1a1a1a;
        }}

        body {{
            font-family: 'DM Mono', monospace;
            font-size: 15px;          /* DM Mono needs bigger base than proportional fonts */
            line-height: 1.6;
            background: var(--parchment);
            color: var(--pitch);
            max-width: 480px;
            margin: 0 auto;
            min-height: 100vh;
        }}

        /* ── Header ─────────────────────────────── */
        .header {{
            background: var(--pitch);
            padding: 32px 28px 28px;
            border-bottom: 4px solid var(--strike);
        }}
        .header-meta {{
            font-size: 11px;
            font-weight: 500;
            color: var(--strike);
            letter-spacing: 0.14em;
            text-transform: uppercase;
            margin-bottom: 10px;
        }}
        .header-title {{
            font-family: 'Syne', sans-serif;
            font-size: 42px;
            font-weight: 800;
            color: var(--parchment);
            line-height: 0.92;
            text-transform: uppercase;
            letter-spacing: -0.02em;
        }}
        .header-sub {{
            font-size: 13px;
            color: var(--granite);
            margin-top: 14px;
            line-height: 1.6;
        }}

        /* ── Sections ────────────────────────────── */
        .section {{
            padding: 0 0 12px;
        }}
        .section-label {{
            display: inline-block;
            font-size: 11px;
            font-weight: 500;
            letter-spacing: 0.12em;
            text-transform: uppercase;
            padding: 6px 14px;
            margin: 24px 28px 0;
            background: var(--pitch);
            color: var(--parchment);
        }}
        .section-label.teal {{
            background: var(--northsea);
            color: var(--pitch);
        }}

        /* ── Event Cards ─────────────────────────── */
        .event-card {{
            border-bottom: 2px solid var(--pitch);
            padding: 22px 28px;
        }}
        .event-header {{
            display: flex;
            align-items: center;
            gap: 10px;
            margin-bottom: 10px;
        }}
        .event-num {{
            font-family: 'Syne', sans-serif;
            font-size: 32px;
            font-weight: 800;
            color: var(--pitch);
            opacity: 0.15;
            line-height: 1;
        }}
        .event-category {{
            font-size: 11px;
            font-weight: 500;
            text-transform: uppercase;
            letter-spacing: 0.1em;
            color: var(--granite);
        }}
        .event-name {{
            font-family: 'Syne', sans-serif;
            font-size: 21px;
            font-weight: 800;
            text-transform: uppercase;
            line-height: 1.05;
            letter-spacing: -0.01em;
            margin-bottom: 12px;
        }}
        .event-meta {{
            display: flex;
            flex-wrap: wrap;
            align-items: center;
            gap: 6px;
            font-size: 13px;
            margin-bottom: 14px;
        }}
        .meta-dot {{ color: var(--granite); }}
        .price-tag {{
            font-size: 12px;
            font-weight: 500;
            padding: 3px 8px;
            margin-left: 4px;
        }}
        .vibe {{
            font-size: 13px;
            font-style: italic;
            color: var(--pitch);
            border-left: 3px solid var(--strike);
            padding-left: 12px;
            line-height: 1.65;
            margin-bottom: 16px;
        }}
        .ticket-btn {{
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
            border: 2px solid var(--pitch);
            margin-top: 4px;
        }}
        .ticket-btn:active {{ background: var(--pitch); color: var(--strike); }}

        /* ── Opening Cards ───────────────────────── */
        .opening-card {{
            background: var(--northsea);
            border-bottom: 2px solid var(--pitch);
            padding: 22px 28px;
        }}
        .opening-source {{
            font-size: 11px;
            font-weight: 500;
            text-transform: uppercase;
            letter-spacing: 0.12em;
            color: var(--pitch);
            opacity: 0.7;
        }}
        .opening-title {{
            font-family: 'Syne', sans-serif;
            font-size: 19px;
            font-weight: 800;
            text-transform: uppercase;
            line-height: 1.1;
            margin: 8px 0 10px;
        }}
        .opening-summary {{
            font-size: 14px;
            line-height: 1.7;
            color: var(--pitch);
            margin-bottom: 14px;
        }}
        .read-more {{
            font-size: 13px;
            font-weight: 500;
            color: var(--pitch);
            text-decoration: none;
            border-bottom: 2px solid var(--pitch);
        }}

        /* ── Newsletter CTA ──────────────────────── */
        .newsletter-cta {{
            background: var(--pitch);
            margin: 24px 28px;
            padding: 28px;
            border: 3px solid var(--strike);
        }}
        .cta-label {{
            font-size: 11px;
            font-weight: 500;
            color: var(--strike);
            letter-spacing: 0.14em;
            text-transform: uppercase;
            margin-bottom: 10px;
        }}
        .cta-headline {{
            font-family: 'Syne', sans-serif;
            font-size: 24px;
            font-weight: 800;
            color: var(--parchment);
            text-transform: uppercase;
            line-height: 1.1;
            margin-bottom: 10px;
        }}
        .cta-body {{
            font-size: 13px;
            color: var(--granite);
            line-height: 1.7;
            margin-bottom: 20px;
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
            padding: 16px 20px;
        }}

        /* ── Footer ──────────────────────────────── */
        .footer {{
            border-top: 3px solid var(--pitch);
            padding: 22px 28px;
            margin-top: 4px;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }}
        .footer-handle {{
            font-family: 'Syne', sans-serif;
            font-size: 16px;
            font-weight: 800;
            text-transform: uppercase;
        }}
        .footer-note {{
            font-size: 12px;
            color: var(--granite);
        }}
    </style>
</head>
<body>

    <header class="header">
        <div class="header-meta">Week of {date_display}</div>
        <div class="header-title">Aberdeen<br>Insider</div>
        <div class="header-sub">Your mate who knows what's good.<br>Every Friday — no filler.</div>
    </header>

    <section class="section">
        <div class="section-label">This Weekend</div>
        {events_html}
    </section>

    {openings_section}

    <div class="newsletter-cta">
        <div class="cta-label">Never Miss a Drop</div>
        <div class="cta-headline">Get it in your inbox every Friday.</div>
        <p class="cta-body">Free weekly newsletter. Aberdeen events, new openings, local tips. Under 3 minutes to read.</p>
        <a href="#" class="cta-btn">Subscribe Free →</a>
    </div>

    <footer class="footer">
        <span class="footer-handle">@abdn.insider</span>
        <span class="footer-note">Updated every Friday</span>
    </footer>

</body>
</html>"""

    # Save to output/newsletters/ (local archive)
    output_dir = Path("output/newsletters")
    output_dir.mkdir(parents=True, exist_ok=True)
    output_path = output_dir / f"linkinbio-{week_of}.html"
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(html)

    # Also save to docs/ — served by GitHub Pages
    # URL: https://graemewal777.github.io/abdn-insider/linkinbio-YYYY-MM-DD.html
    docs_dir = Path("docs")
    docs_dir.mkdir(exist_ok=True)
    docs_path = docs_dir / f"linkinbio-{week_of}.html"
    with open(docs_path, "w", encoding="utf-8") as f:
        f.write(html)

    print(f"✅ Link-in-bio saved to {output_path} + docs/")
    return str(output_path)


if __name__ == "__main__":
    with open("data/combined_weekly.json") as f:
        data = json.load(f)
    generate_linkinbio(data)
