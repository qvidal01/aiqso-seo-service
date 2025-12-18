from __future__ import annotations

from fastapi import Header, HTTPException, Request
from sqlalchemy.orm import Session

from app.config import get_settings
from app.database import SessionLocal
from app.models.client import Client


def _extract_api_key(*, authorization: str | None, x_api_key: str | None) -> str | None:
    if x_api_key:
        return x_api_key.strip()
    if not authorization:
        return None
    # Accept "Bearer <key>" for compatibility with the OpenAPI description in app/main.py
    if authorization.lower().startswith("bearer "):
        return authorization.split(" ", 1)[1].strip() or None
    return None


def require_client(
    request: Request,
    authorization: str | None = Header(default=None, alias="Authorization"),
    x_api_key: str | None = Header(default=None, alias="X-API-Key"),
) -> Client | None:
    """
    Optional API key auth guard.

    - When `REQUIRE_API_KEY=false` (default), this is a no-op and returns `None`.
    - When enabled, it requires either `X-API-Key` or `Authorization: Bearer ...` and
      validates it against `Client.api_key`.
    """
    settings = get_settings()
    if not settings.require_api_key:
        return None

    api_key = _extract_api_key(authorization=authorization, x_api_key=x_api_key)
    if not api_key:
        raise HTTPException(status_code=401, detail="API key required")

    db: Session = SessionLocal()
    try:
        client = db.query(Client).filter(Client.api_key == api_key).first()
        if not client:
            raise HTTPException(status_code=401, detail="Invalid API key")
        return client
    finally:
        db.close()
