# Configuration

## Environment Variables

Copy `.env.example` to `.env` and configure:

```bash
cp .env.example .env
```

### Available Variables

```bash
# Database
DB_PASSWORD=your_secure_password_here

# API Security
SECRET_KEY=generate-a-long-random-string-here

# SerpBear Configuration
SERPBEAR_USER=admin
SERPBEAR_PASSWORD=your_serpbear_password
SERPBEAR_SECRET=generate-another-random-string
SERPBEAR_API_KEY=your_serpbear_api_key
SERPBEAR_URL=http://serpbear:3000
SERPBEAR_PUBLIC_URL=https://serpbear.aiqso.io

# Scraping API (for SERP data - choose one)
# ScrapingAnt: https://scrapingant.com (10k free/month)
# Serper: https://serper.dev
SCRAPING_API_KEY=your_scraping_api_key
SCRAPING_API_PROVIDER=scrapingant

# Anthropic (for AI insights)
ANTHROPIC_API_KEY=your_anthropic_api_key

# AI Server (Ollama on homelab)
AI_SERVER_URL=http://192.168.0.234:11434

# Stripe (for billing)
STRIPE_SECRET_KEY=sk_test_your_stripe_secret_key
STRIPE_PUBLISHABLE_KEY=pk_test_your_stripe_publishable_key
STRIPE_WEBHOOK_SECRET=whsec_your_webhook_secret

# Odoo ERP (for client/invoice management)
ODOO_URL=https://your-company.odoo.com
ODOO_DATABASE=your-database
ODOO_USERNAME=your@email.com
ODOO_API_KEY=your_odoo_api_key

# App URL (for callbacks and webhooks)
APP_URL=https://seo.aiqso.io

# Debug mode
DEBUG=false
ENVIRONMENT=production
DB_AUTO_CREATE=true

# Logging
LOG_LEVEL=INFO
LOG_JSON=false

# API key auth (optional hardening)
```
