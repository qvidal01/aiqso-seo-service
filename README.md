# AIQSO SEO Service

Enterprise SEO auditing, rank tracking, and optimization platform.

## Features

- **Technical SEO Audits**: 24+ checks for meta tags, content, performance, and configuration
- **Rank Tracking**: Daily keyword position monitoring via SerpBear integration
- **Performance Audits**: Google Lighthouse integration for Core Web Vitals
- **AI-Powered Insights**: Content analysis and recommendations using Claude
- **Client Dashboard**: White-label reporting and historical tracking
- **API Access**: RESTful API for integrations

## Architecture

```
┌─────────────────────────────────────────────┐
│         AIQSO Website (Next.js)             │
│         - Service Pages                     │
│         - Client Portal                     │
│         - Admin Dashboard                   │
└─────────────────────────────────────────────┘
                    │
                    ▼
┌─────────────────────────────────────────────┐
│      AIQSO SEO Service (FastAPI)            │
│                                             │
│  ├── /api/audit      - Run SEO audits       │
│  ├── /api/rankings   - Track keywords       │
│  ├── /api/lighthouse - Performance audits   │
│  ├── /api/reports    - Generate reports     │
│  └── /api/clients    - Client management    │
└─────────────────────────────────────────────┘
                    │
        ┌───────────┼───────────┐
        ▼           ▼           ▼
┌──────────┐ ┌──────────┐ ┌──────────┐
│ SerpBear │ │Lighthouse│ │PostgreSQL│
│  :3000   │ │  CI      │ │  :5432   │
└──────────┘ └──────────┘ └──────────┘
```

## Service Tiers

| Tier | Price | Keywords | Sites | Audits | Features |
|------|-------|----------|-------|--------|----------|
| Starter | $500/mo | 50 | 1 | Weekly | Basic reports |
| Professional | $1,500/mo | 200 | 3 | Daily | AI insights |
| Enterprise | $3,500/mo | 500 | 10 | Real-time | Full API |
| Agency | $5,000/mo | 1000+ | Unlimited | Custom | White-label |

## Quick Start

### Local (API only)

```bash
# Install dependencies
pip install -r requirements.txt

# Run development server
uvicorn app.main:app --reload --port 8002
```

### Docker Compose (recommended)

```bash
cp .env.example .env
docker-compose up -d --build
```

- API: `http://localhost:8002` (docs at `/docs`)
- Dashboard: `http://localhost:3000`
- SerpBear: `http://localhost:3001`

## Configuration

Environment variables are loaded via `app/config.py` (Pydantic Settings). A template is provided in `.env.example`.

See `docs/CONFIGURATION.md` for the full list and defaults.

### Minimal Environment Variables

At minimum, set:

- `DATABASE_URL`
- `REDIS_URL` (if running Celery)
- `SECRET_KEY` (required for `staging`/`production`)

```bash
DATABASE_URL=postgresql://user:pass@localhost:5432/seo_service
SERPBEAR_URL=http://localhost:3000
SERPBEAR_API_KEY=your_api_key
SCRAPING_API_KEY=your_scrapingant_key
ANTHROPIC_API_KEY=your_claude_key
```

## Security

- Optional API key enforcement is controlled by `REQUIRE_API_KEY` (default: `false`).
- When enabled, most API routes require either:
  - `X-API-Key: <client api key>` or
  - `Authorization: Bearer <client api key>`

## Deployment

Deploy on Proxmox LXC with Docker Compose:

```bash
docker-compose up -d
```

## Development

### Celery

```bash
celery -A app.celery_app worker --loglevel=info
celery -A app.celery_app beat --loglevel=info
```

Or use `scripts/start_celery.sh`.

### Tests

```bash
pytest -q
```

## Docs

- `ARCHITECTURE.md`
- `docs/CONFIGURATION.md`
- `IMPLEMENTATION_NOTES.md`
- `CHANGELOG.md`

## License

Proprietary - AIQSO LLC
