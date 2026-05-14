from __future__ import annotations

from dataclasses import dataclass

from fastapi import Depends, Header, HTTPException, status

from app.core.config import Settings, get_settings
from app.core.deps import get_supabase_admin_client


@dataclass
class CurrentUser:
    id: str
    email: str | None = None


def _extract_bearer_token(authorization: str | None) -> str | None:
    if not authorization:
        return None
    prefix = "bearer "
    if authorization.lower().startswith(prefix):
        return authorization[len(prefix) :].strip()
    return None


def get_current_user(
    authorization: str | None = Header(default=None),
    settings: Settings = Depends(get_settings),
) -> CurrentUser:
    if settings.use_mock_data:
        return CurrentUser(id="demo-user", email="demo@plantiq.local")

    token = _extract_bearer_token(authorization)
    if not token:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Missing auth token")

    try:
        admin_client = get_supabase_admin_client()
        user_response = admin_client.auth.get_user(token)
        user = user_response.user
    except Exception as exc:  # pragma: no cover - network/auth errors
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid auth token") from exc

    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid auth token")

    return CurrentUser(id=user.id, email=user.email)
