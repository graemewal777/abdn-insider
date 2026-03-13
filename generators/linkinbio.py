"""
Aberdeen Insider — Link-in-Bio Page Generator
Generates a mobile-first HTML page each week: events + affiliate links.
Saved to docs/ for GitHub Pages serving.

Output: docs/linkinbio-YYYY-MM-DD.html
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


def _event_card(event: dict, index: int) -> str:
    price     = event.get("price", "")
    is_free   = price == "Free"
    ticket_url = event.get("url", "")
    category  = event.get("category", "")
    vibe      = event.get("vibe_note", "")

    price_html = ""
    if price:
        bg  = "#0A0A0A" if is_free else "#FFE500"
        col = "#FFE500" if is_free else "#0A0A0A"
        price_html = f'<span class="price" style="background:{bg};color:{col};">{price}</span>'

    vibe_html = f'<p class="vibe">{vibe}</p>' if vibe else ""

    btn_html = ""
    if ticket_url:
        label = "Free — More Info →" if is_free else "Get Tickets →"
        btn_class = "btn-secondary" if is_free else "btn-primary"
        btn_html = f'<a href="{ticket_url}" target="_blank" rel="noopener" class="ticket-btn {btn_class}">{label}</a>'

    return f"""
    <article class="card">
        <div class="card-top">
            <span class="card-num">{index:02d}</span>
            <span class="card-cat">{category}</span>
            {price_html}
        </div>
        <h3 class="card-name">{event.get("name", "")}</h3>
        <div class="card-meta">
            <span>{event.get("venue", "")}</span>
            <span class="dot">·</span>
            <span>{event.get("date", "")}</span>
            <span class="dot">·</span>
            <span>{event.get("time", "")}</span>
        </div>
        {vibe_html}
        {btn_html}
    </article>"""


def _opening_card(item: dict) -> str:
    url = item.get("url", "")
    link_html = f'<a href="{url}" target="_blank" rel="noopener" class="open-link">Read more →</a>' if url else ""
    return f"""
    <article class="card card-opening">
        <span class="open-source">{item.get("source", "")}</span>
        <h3 class="open-title">{item.get("title", "")}</h3>
        <p class="open-body">{item.get("summary", "")[:200]}{"…" if len(item.get("summary","")) > 200 else ""}</p>
        {link_html}
    </article>"""


def generate_linkinbio(data: dict) -> str:
    week_of  = data.get("week_of", datetime.now().strftime("%Y-%m-%d"))
    events   = data.get("events", [])
    openings = data.get("openings", [])

    try:
        dt           = datetime.strptime(week_of, "%Y-%m-%d")
        date_display = dt.strftime("%-d %b %Y").upper()
        week_label   = f"WK {dt.isocalendar()[1]} · {dt.strftime('%b %Y').upper()}"
    except ValueError:
        date_display = week_of.upper()
        week_label   = week_of.upper()

    events_html = "\n".join(_event_card(e, i + 1) for i, e in enumerate(events))
    ga4_html    = _ga4_snippet(GA_TRACKING_ID)

    openings_section = ""
    if openings:
        cards = "\n".join(_opening_card(o) for o in openings)
        openings_section = f"""
    <div class="section-label teal">New In Aberdeen</div>
    {cards}"""

    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Aberdeen Insider — {date_display}</title>
    <meta name="description" content="Aberdeen events this weekend — {date_display}. No filler.">
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Syne:wght@800&family=DM+Mono:ital,wght@0,400;0,500;1,400&display=swap" rel="stylesheet">{ga4_html}
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

        html {{ background: var(--pitch); }}

        body {{
            font-family: 'DM Mono', monospace;
            background: var(--parchment);
            color: var(--pitch);
            max-width: 520px;
            margin: 0 auto;
            min-height: 100vh;
            border-left: 2px solid var(--pitch);
            border-right: 2px solid var(--pitch);
        }}

        a {{ text-decoration: none; color: inherit; }}

        /* ── Header ─────────────────────────────────── */
        .header {{
            background: var(--pitch);
        }}
        .header-stripe {{
            background: var(--strike);
            height: 5px;
        }}
        .header-inner {{
            padding: 24px 24px 22px;
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
            font-size: 40px;
            font-weight: 800;
            color: var(--parchment);
            text-transform: uppercase;
            line-height: 0.92;
            letter-spacing: -0.02em;
        }}
        .header-sub {{
            font-size: 12px;
            color: var(--granite);
            margin-top: 10px;
            letter-spacing: 0.04em;
        }}

        /* ── Section labels ─────────────────────────── */
        .section-label {{
            display: inline-block;
            font-size: 10px;
            font-weight: 500;
            letter-spacing: 0.16em;
            text-transform: uppercase;
            padding: 5px 12px;
            margin: 20px 0 0 0;
            background: var(--pitch);
            color: var(--parchment);
            border-bottom: 2px solid var(--pitch);
            width: 100%;
        }}
        .section-label.teal {{
            background: var(--northsea);
            color: var(--pitch);
        }}

        /* ── Event Cards ─────────────────────────────── */
        .card {{
            padding: 20px 24px;
            border-bottom: 2px solid var(--pitch);
            background: var(--parchment);
        }}
        .card-top {{
            display: flex;
            align-items: center;
            gap: 8px;
            margin-bottom: 8px;
        }}
        .card-num {{
            font-family: 'Syne', sans-serif;
            font-size: 28px;
            font-weight: 800;
            line-height: 1;
            color: var(--pitch);
            opacity: 0.12;
            min-width: 36px;
        }}
        .card-cat {{
            font-size: 10px;
            font-weight: 500;
            letter-spacing: 0.12em;
            text-transform: uppercase;
            color: var(--granite);
            flex: 1;
        }}
        .price {{
            font-size: 11px;
            font-weight: 500;
            letter-spacing: 0.06em;
            padding: 3px 9px;
            white-space: nowrap;
        }}
        .card-name {{
            font-family: 'Syne', sans-serif;
            font-size: 20px;
            font-weight: 800;
            text-transform: uppercase;
            line-height: 1.05;
            letter-spacing: -0.01em;
            margin-bottom: 8px;
        }}
        .card-meta {{
            display: flex;
            flex-wrap: wrap;
            align-items: center;
            gap: 5px;
            font-size: 12px;
            color: var(--granite);
            margin-bottom: 12px;
        }}
        .dot {{ opacity: 0.4; }}
        .vibe {{
            font-size: 13px;
            font-style: italic;
            border-left: 3px solid var(--strike);
            padding-left: 12px;
            line-height: 1.6;
            margin-bottom: 14px;
            color: var(--pitch);
        }}
        .ticket-btn {{
            display: block;
            text-align: center;
            font-size: 13px;
            font-weight: 500;
            letter-spacing: 0.08em;
            text-transform: uppercase;
            padding: 13px 16px;
            border: 2px solid var(--pitch);
        }}
        .btn-primary {{
            background: var(--strike);
            color: var(--pitch);
        }}
        .btn-secondary {{
            background: transparent;
            color: var(--pitch);
        }}

        /* ── Opening Cards ───────────────────────────── */
        .card-opening {{
            background: var(--northsea);
        }}
        .open-source {{
            font-size: 10px;
            font-weight: 500;
            letter-spacing: 0.14em;
            text-transform: uppercase;
            color: var(--pitch);
            opacity: 0.6;
            display: block;
            margin-bottom: 6px;
        }}
        .open-title {{
            font-family: 'Syne', sans-serif;
            font-size: 18px;
            font-weight: 800;
            text-transform: uppercase;
            line-height: 1.1;
            margin-bottom: 8px;
        }}
        .open-body {{
            font-size: 13px;
            line-height: 1.65;
            margin-bottom: 12px;
        }}
        .open-link {{
            font-size: 12px;
            font-weight: 500;
            letter-spacing: 0.06em;
            text-transform: uppercase;
            border-bottom: 2px solid var(--pitch);
        }}

        /* ── Newsletter CTA ──────────────────────────── */
        .newsletter {{
            background: var(--pitch);
            padding: 28px 24px;
            border-top: 3px solid var(--strike);
            margin-top: 4px;
        }}
        .nl-eyebrow {{
            font-size: 10px;
            font-weight: 500;
            color: var(--strike);
            letter-spacing: 0.16em;
            text-transform: uppercase;
            margin-bottom: 8px;
        }}
        .nl-headline {{
            font-family: 'Syne', sans-serif;
            font-size: 28px;
            font-weight: 800;
            color: var(--parchment);
            text-transform: uppercase;
            line-height: 1.0;
            letter-spacing: -0.01em;
            margin-bottom: 10px;
        }}
        .nl-body {{
            font-size: 13px;
            color: var(--granite);
            line-height: 1.7;
            margin-bottom: 20px;
        }}
        .nl-btn {{
            display: block;
            text-align: center;
            background: var(--strike);
            color: var(--pitch);
            font-size: 13px;
            font-weight: 500;
            letter-spacing: 0.08em;
            text-transform: uppercase;
            padding: 15px;
        }}

        /* ── Footer ──────────────────────────────────── */
        .footer {{
            padding: 18px 24px;
            display: flex;
            justify-content: space-between;
            align-items: center;
            border-top: 2px solid var(--pitch);
        }}
        .footer-handle {{
            font-family: 'Syne', sans-serif;
            font-size: 15px;
            font-weight: 800;
            text-transform: uppercase;
        }}
        .footer-note {{
            font-size: 11px;
            color: var(--granite);
            letter-spacing: 0.08em;
            text-transform: uppercase;
        }}
    </style>
</head>
<body>

    <header class="header">
        <div class="header-stripe"></div>
        <div class="header-inner">
            <div class="header-eyebrow">{week_label}</div>
            <div class="header-title">Aberdeen<br>Insider</div>
            <div class="header-sub">Your mate who knows what's good · Every Friday</div>
        </div>
    </header>

    <div class="section-label">This Weekend</div>

    {events_html}

    {openings_section}

    <div class="newsletter">
        <div class="nl-eyebrow">Never Miss a Drop</div>
        <div class="nl-headline">Get it in<br>your inbox.</div>
        <p class="nl-body">Free weekly newsletter. Aberdeen events, new openings, local tips. Under 3 minutes to read.</p>
        <a href="https://abdn-insider.beehiiv.com/subscribe" target="_blank" class="nl-btn">Subscribe Free →</a>
    </div>

    <footer class="footer">
        <span class="footer-handle">@abdn.insider</span>
        <span class="footer-note">Updated every Friday</span>
    </footer>

</body>
</html>"""

    output_dir = Path("output/newsletters")
    output_dir.mkdir(parents=True, exist_ok=True)
    output_path = output_dir / f"linkinbio-{week_of}.html"
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(html)

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
