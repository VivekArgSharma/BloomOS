from __future__ import annotations

from datetime import datetime
from uuid import UUID

from supabase import Client

from app.core.config import Settings


class StorageService:
    def __init__(self, client: Client, settings: Settings) -> None:
        self.client = client
        self.settings = settings

    def upload_plant_photo(self, plant_id: UUID, filename: str, content: bytes, content_type: str) -> str:
        safe_name = filename.replace(" ", "-") or "upload.jpg"
        path = f"{plant_id}/{datetime.utcnow().strftime('%Y%m%d%H%M%S')}-{safe_name}"
        bucket = self.client.storage.from_(self.settings.supabase_storage_bucket)
        bucket.upload(path, content, {"content-type": content_type, "upsert": "true"})
        return f"{self.settings.supabase_url}/storage/v1/object/public/{self.settings.supabase_storage_bucket}/{path}"
