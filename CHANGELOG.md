# Changelog

All notable changes to this repository are documented in this file.

## Unreleased

### Added
- Runtime configuration validation (`ENVIRONMENT`, `SECRET_KEY` checks) and logging configuration (`LOG_LEVEL`, `LOG_JSON`).
- Optional API key enforcement for most routes via `REQUIRE_API_KEY`.
- Minimal pytest coverage for settings validation and health endpoint.
- Documentation: `ARCHITECTURE.md`, `docs/CONFIGURATION.md`, `IMPLEMENTATION_NOTES.md`.

### Changed
- `/health/db` now uses SQLAlchemy `text()` and returns `503` when unhealthy.
- Reduced stdout `print()` usage in favor of structured logging.

### Fixed
- Added missing runtime dependencies used by the codebase (`PyYAML`, `click`) to `requirements.txt`.

