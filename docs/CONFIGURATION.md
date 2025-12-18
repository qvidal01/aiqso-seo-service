# Configuration

This service is configured entirely via environment variables (optionally loaded from a `.env` file). A template is provided in `.env.example`.

## Core

- `ENVIRONMENT` (`development|staging|production|test`, default: `development`)
  - Enables stricter validation in `staging`/`production`.
- `DEBUG` (default: `false`)
  - When `true`, SQLAlchemy echo and other debug behaviors may be enabled.
- `APP_URL` (default: `https://seo.aiqso.io`)
  - Used for Stripe callback URLs and links.
- `CORS_ORIGINS` (default: `http://localhost:3000,https://aiqso.io`)
  - Comma-separated list of allowed origins.

## Database / Redis

- `DATABASE_URL` (default: `postgresql://seo_user:seo_pass@localhost:5432/aiqso_seo`)
- `REDIS_URL` (default: `redis://localhost:6379/0`)
- `DB_AUTO_CREATE` (default: `true`)
  - When `true`, the backend calls `Base.metadata.create_all()` on startup.
  - For production, prefer migrations and set `DB_AUTO_CREATE=false`.

## Security

- `SECRET_KEY` (default: `change-this-in-production`)
  - Required to be a long random value in `staging`/`production`.
- `REQUIRE_API_KEY` (default: `false`)
  - When `true`, most API routes require either:
    - `X-API-Key: <client api key>`, or
    - `Authorization: Bearer <client api key>`

## Logging

- `LOG_LEVEL` (default: `INFO`)
- `LOG_JSON` (default: `false`)
  - When `true`, emit JSON logs to stdout (container-friendly).

## Integrations

### SerpBear

- `SERPBEAR_URL` (default: `http://localhost:3000`)
- `SERPBEAR_API_KEY` (default: empty)
- `SCRAPING_API_KEY` (default: empty)
- `SCRAPING_API_PROVIDER` (default: `scrapingant`)

### AI

- `ANTHROPIC_API_KEY` (default: empty)
- `AI_SERVER_URL` (default: `https://ai-api.aiqso.io`)

### Stripe

- `STRIPE_SECRET_KEY` (default: empty)
- `STRIPE_PUBLISHABLE_KEY` (default: empty)
- `STRIPE_WEBHOOK_SECRET` (default: empty)

### Odoo

- `ODOO_URL` (default: empty)
- `ODOO_DATABASE` (default: empty)
- `ODOO_USERNAME` (default: empty)
- `ODOO_API_KEY` (default: empty)

