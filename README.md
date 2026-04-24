# AISEO — AI Agent SEO Score

Paste any URL and get a score, grade, and fix list for how well AI agents can find and cite your site. Like SEO, but for AI.

## What It Checks

| Category | Checks |
|---|---|
| **Agent Access** | robots.txt, llms.txt, llms-full.txt, X-Robots-Tag, HTTP status |
| **Discoverability** | Sitemap.xml |
| **Structured Data** | JSON-LD / Schema.org |
| **Content Clarity** | Title, meta description, OG tags, headings, semantic HTML, text-to-HTML ratio |
| **Trust & Security** | HTTPS, canonical URL |

## Stack

- **Backend**: Python, FastAPI, httpx, BeautifulSoup
- **Frontend**: React, TypeScript, Vite, Tailwind CSS
- **Tests**: pytest + respx (backend), TypeScript type-check (frontend)
- **CI**: GitHub Actions

## Quick Start

### Backend

```bash
cd backend
python -m venv .venv && source .venv/bin/activate
pip install -e ".[dev]"
uvicorn app.main:app --reload
```

### Frontend

```bash
cd frontend
npm install
npm run dev
```

The frontend dev server proxies `/api` requests to `localhost:8000`.

### Run Tests

```bash
# Backend
cd backend && source .venv/bin/activate && pytest tests/ -v

# Frontend
cd frontend && npx tsc --noEmit
```

## How Scoring Works

Each check has a **weight** (0-1) and produces a **score** (0-100). The overall score is a weighted average across all checks. Grades map to score ranges:

- **A**: 90-100
- **B**: 75-89
- **C**: 60-74
- **D**: 40-59
- **F**: 0-39

## API

### `POST /api/scan`

```json
{
  "url": "https://example.com"
}
```

Returns: score, grade, category breakdown with individual check results, and a prioritised fix list with code snippets.

## Environment Variables

| Variable | Description | Default |
|---|---|---|
| `VITE_API_BASE` | Backend API URL for production frontend | `""` (same origin) |
