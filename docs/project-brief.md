# Aberdeen Insider — Claude Code Project Brief
**Handle:** @abdn.insider
**Goal:** Fully automated weekly content pipeline surfacing Aberdeen events, venues & lifestyle content for Instagram + Newsletter
**Target audience:** Aberdeen 22–40 young professionals
**Tone:** Local, sharp, slightly edgy — "your mate who knows what's good"

---

## Project Structure

```
aberdeen-insider/
├── scrapers/
│   ├── skiddle.py          # Events scraper
│   ├── eventbrite.py       # Secondary events
│   ├── rss_scraper.py      # Aberdeen Live / P&J / Aberdeen Business News
│   └── google_places.py    # Venue enrichment
├── data/
│   ├── events.json
│   ├── venues.json
│   └── combined_weekly.json
├── generators/
│   ├── carousel.py         # Instagram carousel HTML generator
│   ├── caption.py          # Caption + hashtag generator
│   └── newsletter.py       # Weekly newsletter HTML generator
├── assets/
│   └── fonts/              # Inter or Space Grotesk
├── output/
│   ├── carousels/          # Weekly carousel HTML files
│   └── newsletters/        # Weekly newsletter HTML files
├── scheduler.py            # Runs full pipeline weekly
├── config.py               # API keys, settings
└── README.md
```

---

## Phase 1 — Build This First

### 1. Skiddle Scraper (`scrapers/skiddle.py`)
- Scrape Aberdeen events for the coming weekend (Fri–Sun)
- Fields: `name`, `date`, `time`, `venue`, `category`, `price`, `url`, `vibe_note`
- Categories: Nightlife, Live Music, Comedy, Food & Drink, Arts, Sport
- Affiliate URL format: append Skiddle affiliate ID to event URLs
- Return as structured JSON

### 2. RSS Scraper (`scrapers/rss_scraper.py`)
- Sources:
  - Aberdeen Live: `https://www.aberdeenlive.news/news/?service=rss`
  - Aberdeen Business News: `https://www.aberdeen-business.com/feed/`
  - P&J: `https://www.pressandjournal.co.uk/feed/`
- Filter for: new venue openings, events, food & drink, nightlife
- Fields: `title`, `summary`, `url`, `date`, `category`

### 3. Combined Data Pipeline (`scheduler.py`)
- Runs both scrapers
- Deduplicates and merges
- Tags each item: `type` (event | opening | news), `weekend_relevant` (bool)
- Saves to `data/combined_weekly.json`
- Designed to run on a weekly cron (Friday morning)

---

## Phase 2 — Content Generation

### Instagram Carousel Generator (`generators/carousel.py`)
Generate a 7-slide HTML carousel (1080x1080px each):

**Visual Style — Neobrutalist:**
- Background: White `#FFFFFF` or Black `#000000` alternating
- Typography: Space Grotesk or Inter, heavy weight (800)
- Accents: Bright yellow `#FFE500` or neon green `#00FF87`
- Borders: 3–4px solid black on white slides
- No gradients, no drop shadows, no rounded corners
- Bold large numbers for list slides

**Slide Structure:**
1. **Cover** — "THIS WEEKEND IN ABERDEEN 🔥" + date range
2. **Event 1** — Name, venue, time, price, vibe note
3. **Event 2** — Same format
4. **Event 3** — Same format
5. **New Opening** — Venue spotlight
6. **Wildcard** — Hidden gem / local tip
7. **CTA** — "Follow for weekly drops" + @abdn.insider

**Output:** One HTML file per slide, plus a `preview_all.html` showing all 7 together

### Caption Generator (`generators/caption.py`)
- Generate Instagram caption for the carousel post
- Tone: punchy, local, no cringe
- Include: top 3 event names, relevant hashtags
- Hashtag set: `#aberdeen #aberdeenscotland #aberdeenevents #thingstodoaberdeen #aberdeenlife #weekendinaberdeen #abdn #aberdeenfood #aberdeennightlife #visitaberdeen`
- Max 2200 characters

---

## Phase 3 — Auto Posting (add after Phase 1 & 2 working)

### Buffer API Integration
- POST to Buffer queue via API
- Schedule: Friday 6pm, Saturday 10am, Sunday 12pm
- Include caption + image (screenshot of carousel slide 1)
- Docs: https://buffer.com/developers/api

---

## APIs to Set Up

| API | Purpose | Cost | Priority |
|-----|---------|------|----------|
| Skiddle Affiliate | Event data + monetisation | Free | 🔴 Do first |
| Eventbrite | Secondary event source | Free | 🟡 Phase 2 |
| Google Places | Venue enrichment | Free tier | 🟡 Phase 2 |
| TikTok Research API | Creator discovery | Free (apply) | 🟢 Phase 3 |
| Buffer API | Auto-posting | Free tier | 🟡 Phase 2 |

---

## Creator Sourcing (Phase 3)

- TikTok Research API: search `#aberdeen` `#aberdeenscotland` `#aberdeenfood`
- Filter: 1k–50k followers (micro-influencers), Aberdeen location
- Output: CSV of creator handles, follower count, engagement rate, contact
- Goal: Build outreach list of 20–30 Aberdeen creators for collab / reposts

---

## Config (`config.py`)
```python
SKIDDLE_API_KEY = ""
EVENTBRITE_API_KEY = ""
GOOGLE_PLACES_API_KEY = ""
BUFFER_ACCESS_TOKEN = ""
TIKTOK_CLIENT_KEY = ""

CITY = "Aberdeen"
CITY_LAT = 57.1497
CITY_LNG = -2.0943
AFFILIATE_ID = ""  # Skiddle affiliate ID

# Posting schedule (Buffer)
POST_TIMES = ["Friday 18:00", "Saturday 10:00", "Sunday 12:00"]
```

---

## First Claude Code Prompt

Use this to kick off the session:

> "I'm building Aberdeen Insider — an automated Instagram content pipeline for Aberdeen events and venues. Create the project folder structure from the brief, then build Phase 1: a Skiddle events scraper and RSS scraper for Aberdeen news sources, combining output into a structured weekly JSON file. Use Python. Add a README with setup instructions."

---

## 90 Day Milestones

| Week | Goal |
|------|------|
| 1–2 | Pipeline runs locally, generates carousel HTML |
| 3–4 | Buffer auto-posting live, 3 posts/week |
| 5–6 | Newsletter HTML generator built, Beehiiv signup linked |
| 7–8 | TikTok creator list built, first DM outreach |
| 9–10 | First Skiddle affiliate click tracked |
| 11–12 | First creator repost / collab, 500+ Instagram followers |
