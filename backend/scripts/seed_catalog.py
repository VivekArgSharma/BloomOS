from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))


from app.db.seed_catalog import PLANT_CATALOG


def main() -> None:
    print(f"Prepared {len(PLANT_CATALOG)} catalog entries for seeding.")
    print("Wire this script to a Supabase upsert once your credentials are populated in backend/.env.")


if __name__ == "__main__":
    main()
