# PlantIQ

PlantIQ is a Supabase + FastAPI + Gemini plant care app built from the supplied `plan.md` and `PRD.md`.

## What is included

- `backend/` FastAPI app with:
  - Supabase-backed gardens, plants, logs, plans, analytics, and catalog routes
  - Gemini-based plant identification, photo analysis, task planning, and chat
  - Supabase Storage photo uploads
  - preloaded catalog of 52 common horticulture plants
  - RAG document folders and ingestion script for your PDFs
- `frontend/` React + Vite dashboard scaffold with:
  - Supabase auth pages
  - live garden and plant dashboards
  - real file upload for onboarding and daily photo analysis
  - analytics charts, diary timeline, and contextual chat panel
- `supabase/migrations/001_init.sql` and `supabase/migrations/002_storage_and_catalog.sql`

## Environment files

Copy these and fill in your keys:

- `backend/.env.example` -> `backend/.env`
- `frontend/.env.example` -> `frontend/.env`

Important Supabase fields:

- `SUPABASE_URL`
- `SUPABASE_ANON_KEY`
- `SUPABASE_SERVICE_ROLE_KEY` backend only

Redis is not required for this scaffold. If you want caching later, you can optionally add `REDIS_URL`, but nothing currently depends on it.

Important backend flags:

- `USE_MOCK_DATA=false` for the finished Supabase-backed product
- `SUPABASE_STORAGE_BUCKET=plant-photos`

## RAG workflow

Yes, there is a folder for your PDFs.

1. Put source PDFs into `backend/data/rag_docs`
2. Run `python scripts/ingest_rag.py` from `backend/`
3. The ingestion manifest is written into `backend/data/faiss_index`
4. Replace the placeholder manifest-only ingest with full embeddings + FAISS persistence when your corpus is finalized

## Quick start

### 1. Run the Supabase migrations

Run both SQL files in order:

- `supabase/migrations/001_init.sql`
- `supabase/migrations/002_storage_and_catalog.sql`

### 2. Seed the preloaded plant catalog

```bash
cd backend
python scripts/seed_catalog.py
```

### 3. Start the backend

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

### 4. Start the frontend

```bash
npm install
npm run dev
```

## Notes

- Set `USE_MOCK_DATA=true` only if you want to temporarily fall back to local demo data.
- Redis is optional and not required in either `.env` file.
- `backend/scripts/seed_catalog.py` now inserts or updates the real `plant_catalog` table.
- Upload plant photos from the Garden and Plant pages after signing in with Supabase.
- Add your RAG PDFs later to `backend/data/rag_docs`, then run `python scripts/ingest_rag.py`.
