# Aberdeen Insider 🏙️
### @abdn.insider — Automated weekly events & lifestyle content for Aberdeen

---

## What This Does
Automated pipeline that runs every Friday and outputs:
- Instagram carousel HTML (7 slides, ready to screenshot & post)
- Instagram caption with hashtags
- Weekly newsletter HTML *(Phase 2)*
- Auto-posts via Buffer *(Phase 2)*

## Setup

### 1. Install dependencies
```bash
pip install requests beautifulsoup4 feedparser python-dotenv
```

### 2. Add API keys
Edit `config.py` and fill in your keys:
- Skiddle Affiliate API key + affiliate ID
- Ticketmaster Discovery API key
- Google Places API key *(Phase 2)*
- Buffer access token *(Phase 2)*

### 3. Connect Paper MCP (for design work)
```bash
claude mcp add paper --transport http http://127.0.0.1:29979/mcp --scope user
```
Make sure Paper Desktop is open with your carousel design file.

### 4. Run the pipeline
```bash
python scheduler.py          # Full pipeline
python scheduler.py --scrape     # Data only
python scheduler.py --generate   # Content only
```

---

## Project Structure
```
aberdeen-insider/
├── scrapers/           Data collection
├── generators/         Content generation
├── data/               JSON output
├── output/             Carousels + newsletters
├── docs/               Style guide + brief
├── scheduler.py        Pipeline entry point
├── config.py           API keys & settings
└── CLAUDE.md           Context for Claude Code
```

## Phases

| Phase | Goal | Status |
|-------|------|--------|
| 1 | Scrapers + carousel generator working locally | 🔨 Building |
| 2 | Buffer auto-posting, 3x/week | ⏳ Next |
| 3 | Newsletter + Beehiiv signup | ⏳ Later |
| 4 | TikTok creator discovery + outreach | ⏳ Later |

## Visual Style
See `docs/styleguide.html` — open in browser.
Neobrutalist editorial. Syne + DM Mono. Hard borders, no rounded corners.

---

*Aberdeen Insider — Built with Claude Code*
