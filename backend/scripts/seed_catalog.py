from pathlib import Path
import sys

from supabase import create_client


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))


from app.core.config import get_settings
from app.db.seed_catalog import PLANT_CATALOG


def main() -> None:
    settings = get_settings()
    if not settings.supabase_url or not settings.supabase_service_role_key:
        raise RuntimeError("SUPABASE_URL and SUPABASE_SERVICE_ROLE_KEY are required to seed the catalog")

    client = create_client(settings.supabase_url, settings.supabase_service_role_key)
    payload = [
        {
            "common_name": item.common_name,
            "species_name": item.species_name,
            "difficulty": item.difficulty,
            "tags": item.tags,
            "care_profile": item.care_profile.model_dump(),
        }
        for item in PLANT_CATALOG
    ]
    existing = client.table("plant_catalog").select("id,species_name").execute().data or []
    existing_by_species = {row["species_name"]: row["id"] for row in existing}

    inserts = []
    for item in payload:
        existing_id = existing_by_species.get(item["species_name"])
        if existing_id:
            client.table("plant_catalog").update(item).eq("id", existing_id).execute()
        else:
            inserts.append(item)

    if inserts:
        client.table("plant_catalog").insert(inserts).execute()
    print(f"Seeded {len(payload)} catalog entries into plant_catalog.")


if __name__ == "__main__":
    main()
