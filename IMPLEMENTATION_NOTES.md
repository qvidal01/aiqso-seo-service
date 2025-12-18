# Implementation Notes

## Why add runtime config validation?

The repo contains production deployment artifacts (Docker Compose, `Dockerfile.backend`) but also ships with insecure defaults (e.g., `SECRET_KEY=change-this-in-production`). In development this is convenient, but in staging/production it becomes a footgun.

The `Settings.validate_runtime()` method is a lightweight guardrail:
- In `staging`/`production`, it fails fast when the configuration is obviously unsafe.
- In `development`/`test`, it stays permissive to keep local iteration easy.

## Why keep `DB_AUTO_CREATE` defaulting to true?

The current behavior creates tables at startup via SQLAlchemy metadata. This is convenient and preserves backward compatibility, even though migrations are typically preferred for production. Instead of forcing a breaking migration workflow, `DB_AUTO_CREATE` makes the behavior explicit and allows production hardening by setting `DB_AUTO_CREATE=false`.

## Why optional API key enforcement?

The codebase already supports per-client API keys (`Client.api_key`) and uses them for some endpoints. Documentation also claims Bearer token authentication, but most routes were previously unauthenticated.

To avoid breaking existing users, auth enforcement is opt-in:
- `REQUIRE_API_KEY=false` (default): no behavior change.
- `REQUIRE_API_KEY=true`: most API routes require `X-API-Key` or `Authorization: Bearer ...`.

## Why add `PyYAML` and `click` to `requirements.txt`?

The code imports `yaml` (`src/core/tiers.py`) and `click` (`src/cli/main.py`). Without explicit dependencies, clean installs fail at runtime. Both are small, stable dependencies and are required to run the shipped features.

