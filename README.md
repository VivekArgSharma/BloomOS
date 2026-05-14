# PlantIQ

PlantIQ is an AI-assisted plant care scaffold built from the supplied `plan.md` and `PRD.md`.

## What is included

- `backend/` FastAPI API scaffold with:
  - garden, plant, weather, chat, and daily task routes
  - mock demo store so the app runs before Supabase is connected
  - preloaded catalog of 50 common horticulture plants
  - RAG document folders and ingestion script
- `frontend/` React + Vite dashboard scaffold with:
  - dashboard, garden, plant, and auth pages
  - catalog preview and quick-add flow
  - daily task completion, diary timeline, and contextual chat panel
- `supabase/migrations/001_init.sql` starter schema with RLS policies

## Environment files

Copy these and fill in your keys:

- `backend/.env.example` -> `backend/.env`
- `frontend/.env.example` -> `frontend/.env`

Important Supabase fields:

- `SUPABASE_URL`
- `SUPABASE_ANON_KEY`
- `SUPABASE_SERVICE_ROLE_KEY` backend only

Redis is not required for this scaffold. If you want caching later, you can optionally add `REDIS_URL`, but nothing currently depends on it.

## RAG workflow

Yes, there is a folder for your PDFs.

1. Put source PDFs into `backend/data/rag_docs`
2. Run `python scripts/ingest_rag.py` from `backend/`
3. The ingestion manifest is written into `backend/data/faiss_index`
4. Replace the placeholder manifest-only ingest with full embeddings + FAISS persistence when your corpus is finalized

## Quick start

### Backend

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

### Frontend

```bash
npm install
npm run dev
```

## Notes

- The current backend defaults to `USE_MOCK_DATA=true` so you can explore the UI immediately.
- Redis is optional and not required in either `.env` file.
- Once Supabase is configured, replace the mock store with repository calls and upsert the catalog into `plant_catalog`.
- `backend/scripts/seed_catalog.py` is the handoff point for catalog seeding.
