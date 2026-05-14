from __future__ import annotations

from functools import lru_cache

from fastapi import Depends
from supabase import Client, create_client

from app.core.config import Settings, get_settings
from app.db.mock_store import MockStore
from app.db.supabase_repo import SupabaseRepository


@lru_cache
def get_mock_store() -> MockStore:
    return MockStore()


@lru_cache
def get_supabase_admin_client() -> Client:
    settings = get_settings()
    if not settings.supabase_url or not settings.supabase_service_role_key:
        raise RuntimeError("SUPABASE_URL and SUPABASE_SERVICE_ROLE_KEY must be configured")
    return create_client(settings.supabase_url, settings.supabase_service_role_key)


@lru_cache
def get_supabase_repository() -> SupabaseRepository:
    settings = get_settings()
    return SupabaseRepository(client=get_supabase_admin_client(), settings=settings)


def get_store(settings: Settings = Depends(get_settings)):
    if settings.use_mock_data:
        return get_mock_store()
    return get_supabase_repository()
