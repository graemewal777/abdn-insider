# Aberdeen Insider — Claude Code Context

## What This Project Is
Aberdeen Insider (@abdn.insider) is an automated local content pipeline for Aberdeen, Scotland.
It scrapes events and venue data, generates Instagram carousels and newsletter content, and
posts on a weekly schedule. Target audience: Aberdeen 22–40 young professionals.

## Goal
Fully automated weekly output every Friday — no manual input required once running.

## Tone & Voice
- "Your mate who knows what's good in Aberdeen"
- Sharp, local, slightly edgy — not corporate, not cringe
- Gen-Z friendly but not try-hard

---

## Visual Style (Neobrutalist Editorial)

Full interactive style guide is in: `docs/styleguide.html` — open in browser for reference.

### Colours
| Name       | Hex       | Use                              |
|------------|-----------|----------------------------------|
| Pitch      | #0A0A0A   | Primary bg, text, borders        |
| Parchment  | #F5F0E8   | Light slides, page bg            |
| Strike     | #FFE500   | Primary accent, CTA              |
| North Sea  | #00C4CC   | New opening slides only          |
| Granite    | #8C8C8C   | Secondary text, labels           |
| Alert      | #FF3B30   | Sold out, urgent tags            |

### Fonts
- **Display/Headlines:** Syne 800 (Google Fonts)
- **Body/Labels/Mono:** DM Mono 400/500 (Google Fonts)
- Import: `https://fonts.googleapis.com/css2?family=Syne:wght@400;700;800&family=DM+Mono:ital,wght@0,400;0,500;1,400&display=swap`

### Carousel Slides (1080×1080px HTML)
- Hard borders only: 3–4px solid #0A0A0A
- No rounded corners, no drop shadows, no gradients
- Tight headline leading: 0.9–1.0
- ALL CAPS for slide titles and CTA
- Max 1 emoji per slide
- Big oversized numbers on list slides (outlined/stroke effect)
- Vibe notes: DM Mono italic, border-left yellow accent

### Slide Colour Logic
1. Cover → Black bg, yellow accent
2. Event slides → Parchment bg, black text
3. New Opening → North Sea (#00C4CC) bg
4. CTA → Yellow bg, black text

---

## Paper MCP Integration

Paper Desktop app is installed and the MCP server is connected.
Connect command: `claude mcp add paper --transport http http://127.0.0.1:29979/mcp --scope user`

### How to use Paper in this project:
- Carousel slide designs live in Paper — use `get_jsx` to pull Tailwind/HTML from designs
- When generating carousel HTML, first check if a Paper design exists for that slide type
- Use `get_computed_styles` to extract exact colours, spacing, font sizes from Paper frames
- Use `get_screenshot` to preview what a slide looks like before writing code
- When a slide is approved, use `write_html` to push updates back to Paper if needed

---

## Project Structure
```
aberdeen-insider/
├── scrapers/
│   ├── skiddle.py          # Events scraper
│   ├── eventbrite.py       # Secondary events
│   ├── rss_scraper.py      # Aberdeen Live / P&J / Aberdeen Business News
│   └── google_places.py    # Venue enrichment
├── generators/
│   ├── carousel.py         # Instagram carousel HTML generator
│   ├── caption.py          # Caption + hashtag generator
│   └── newsletter.py       # Weekly newsletter HTML generator
├── data/
│   ├── events.json
│   ├── venues.json
│   └── combined_weekly.json
├── output/
│   ├── carousels/          # Weekly carousel HTML files
│   └── newsletters/        # Weekly newsletter HTML
├── assets/
│   └── fonts/
├── docs/
│   ├── styleguide.html     # Visual style reference
│   └── project-brief.md    # Full project brief
├── scheduler.py            # Runs full pipeline weekly
├── config.py               # API keys and settings
└── CLAUDE.md               # This file
```

## Key Files
- `config.py` — all API keys and settings, never hardcode keys
- `data/combined_weekly.json` — master data file consumed by generators
- `scheduler.py` — entry point to run the full pipeline
- `docs/styleguide.html` — visual reference, open in browser

## Data Sources
- **Skiddle** — primary events (affiliate links for monetisation)
- **Eventbrite** — secondary events
- **RSS** — Aberdeen Live, Aberdeen Business News, Press & Journal
- **Google Places** — venue enrichment

## APIs
| API               | Purpose              | Status       |
|-------------------|----------------------|--------------|
| Skiddle Affiliate | Events + revenue     | Applied ⏳   |
| Eventbrite        | Secondary events     | To set up    |
| Google Places     | Venue data           | To set up    |
| Buffer            | Auto-posting         | Phase 2      |
| TikTok Research   | Creator discovery    | Phase 3      |

## Coding Conventions
- Python 3.11+
- `requests` for HTTP, `beautifulsoup4` for scraping
- All scrapers return list of dicts with consistent field names
- Always handle rate limits and failed requests gracefully
- Credentials in `config.py` only — never hardcoded
- JSON output always includes a `scraped_at` timestamp

## Current Phase
**Phase 1** — Building scrapers + carousel generator. Nothing live yet.

## Do Not
- Hardcode API keys anywhere
- Use paid libraries unless asked
- Round corners, add shadows or gradients
- Change visual style without checking styleguide.html first
- Over-engineer — working beats clever
