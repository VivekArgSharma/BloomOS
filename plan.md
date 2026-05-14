# PlantIQ - Detailed Implementation Plan

## 1. System Architecture & Tech Stack

### Frontend
- **Framework**: React (Vite)
- **Styling**: Tailwind CSS + Framer Motion (Animations)
- **Data Fetching/State Management**: React Query, Zustand (Global state)
- **Routing**: React Router
- **Deployment**: Vercel

### Backend
- **Framework**: FastAPI (Python)
- **AI/LLM**: Gemini 1.5 Flash / Flash Lite (via Google GenAI SDK)
- **Agent Framework**: LangGraph (for complex reasoning pipelines & daily planning)
- **Vector DB**: FAISS + sentence-transformers (for RAG)
- **Database & Auth**: Supabase (PostgreSQL, Storage, Auth)
- **Caching**: Redis (or Supabase Cache/In-memory)
- **Deployment**: Render

---

## 2. Phase 1: Initial Setup & Configuration

### 2.1 Backend Setup
1. Initialize Python project (`pip`, `virtualenv` or `poetry`).
2. Install dependencies: `fastapi`, `uvicorn`, `supabase`, `langchain`, `langgraph`, `google-genai`, `faiss-cpu`, `sentence-transformers`, `redis`, `httpx`.
3. Set up environment variables (`.env`):
   - `SUPABASE_URL`, `SUPABASE_KEY`
   - `GEMINI_API_KEY`
   - `OPENWEATHERMAP_API_KEY`
   - `REDIS_URL`
4. Create modular folder structure:
   ```text
   backend/
   ├── app/
   │   ├── api/          # FastAPI Route handlers
   │   ├── core/         # Config, security, environment vars
   │   ├── db/           # Supabase client, models
   │   ├── services/     # AI pipelines, Weather fetching, Image compression
   │   ├── agents/       # LangGraph implementations (Daily Planner)
   │   ├── rag/          # FAISS index and embedding logic
   │   └── main.py       # Application entry point
   ```

### 2.2 Frontend Setup
1. Initialize React project: `npm create vite@latest frontend -- --template react-ts`
2. Install dependencies: `tailwindcss`, `framer-motion`, `@tanstack/react-query`, `zustand`, `react-router-dom`, `lucide-react` (icons), `axios`.
3. Setup Tailwind CSS configuration for a modern, organic, dark/light theme (green accents).
4. Set up environment variables (`.env`):
   - `VITE_API_BASE_URL` (FastAPI backend url)
   - `VITE_SUPABASE_URL`, `VITE_SUPABASE_ANON_KEY` (for client-side auth/storage)
5. Create folder structure:
   ```text
   frontend/
   ├── src/
   │   ├── assets/       # Images, global styles
   │   ├── components/   # Reusable UI (Buttons, Cards, Modals, Skeleton Loaders)
   │   ├── pages/        # Route components (Dashboard, GardenView, PlantDetails)
   │   ├── services/     # API clients (axios config)
   │   ├── store/        # Zustand stores for global UI state
   │   ├── hooks/        # Custom React hooks (React Query wrappers)
   │   ├── utils/        # Helpers, formatters
   │   ├── App.tsx
   │   └── main.tsx
   ```

### 2.3 Database Setup (Supabase)
1. Initialize Supabase project.
2. Enable Authentication (Email/Password or OAuth).
3. Create Storage Bucket: `plant-photos`.
4. Execute SQL migrations for schema:
   - **Users**: Extended user preferences and streaks.
   - **Gardens**: `id`, `user_id`, `name`, `location_type` (balcony, indoor, etc.), `created_at`.
   - **Plants**: `id`, `garden_id`, `species_name`, `care_profile` (JSON), `current_health_score`, `recovery_mode` (boolean).
   - **DailyLogs**: `id`, `plant_id`, `photo_url`, `health_score`, `analysis_json` (issues, moisture), `observations`, `date`.
   - **DailyPlans**: `id`, `plant_id`, `date`, `tasks` (JSON array), `weather_snapshot` (JSON), `generated_by_ai` (boolean).
   - **PlantCatalog**: `id`, `common_name`, `species_name`, `care_profile` (JSON), `difficulty`, `tags`.

---

## 3. Phase 2: Core Backend Services & AI Pipelines

### 3.1 Plant Catalog & Onboarding API (Pipeline 1)
- **POST `/api/plants/identify`**: Accepts image upload. Uses `gemini-1.5-flash` to identify plant species, detect difficulty, and generate a standardized care profile.
- **GET `/api/catalog`**: Fetches predefined plants from `PlantCatalog` to allow users to skip image upload (saves API costs).
- **POST `/api/plants`**: Assigns a new plant to a user's specific garden.

### 3.2 Daily AI Task Engine (LangGraph - Pipeline 4)
- Build a LangGraph workflow (`agents/planner.py`) that evaluates each plant daily.
- **Graph Nodes**:
  1. `LoadContext`: Fetch plant details, recent logs, current base care plan.
  2. `FetchWeather`: Call OpenWeatherMap API for location.
  3. `EvaluateHealth`: Check recent trend in `DailyLogs`.
  4. `GenerateTasks`: Use Gemini to formulate contextual daily tasks (e.g., "Skip watering due to rain").
  5. `SaveState`: Update `DailyPlans` in the DB.

### 3.3 Daily Photo Analysis Service (Pipeline 2)
- **POST `/api/plants/{id}/analyze`**: Accepts daily photo.
- Workflow:
  1. Upload image to Supabase Storage.
  2. Call Gemini Vision with image to analyze: health, yellowing, wilting, soil appearance.
  3. Parse structured JSON output (health score 1-10, visible issues, soil moisture estimate).
  4. Save to `DailyLogs` table.
  5. **Recovery Mode Trigger**: If score drops < 5, trigger planner to increase monitoring frequency and adjust watering schedules.

### 3.4 RAG-Based Plant Knowledge System (Pipeline 3)
- **Setup FAISS Offline**: Process PDFs of plant care guides, chunk using LangChain, embed via `sentence-transformers`, save FAISS index locally.
- **POST `/api/chat`**:
  1. Receive user query + plant context ID.
  2. Embed query -> FAISS similarity search.
  3. Inject top-K chunks + recent `DailyLogs` into Gemini prompt.
  4. Stream grounded response back to frontend.

---

## 4. Phase 3: Frontend Development (MVP Scope)

### 4.1 Authentication & Main Layout
- Implement Supabase Auth UI (Login/Register/Magic Links).
- Create Main Layout with Bottom Navigation for mobile-first usage.

### 4.2 Dashboard & Multi-Garden Management
- **Dashboard (`/`)**: 
  - Displays summary of all user gardens.
  - Overall aggregated health score.
  - Quick summary of pending daily tasks across all plants.
- **Garden View (`/garden/{id}`)**: 
  - Grid list of plants in a specific garden.
  - Weather summary pill (e.g., "Sunny, 28°C").
  - Alerts and warnings (e.g., "2 Plants in Recovery Mode").

### 4.3 Plant Onboarding Flow (Modal/Wizard)
- Multi-step Framer Motion animated wizard:
  1. **Method Selection**: "Take a Photo" or "Search Catalog".
  2. **Image Processing State**: Show skeleton loaders and educational tips while Gemini identifies the plant.
  3. **Review Care Profile**: Display AI-generated schedule, confirm garden placement, and finalize.

### 4.4 Plant Details & Visual Timeline
- **Plant View (`/plant/{id}`)**:
  - Current Health Score with color-coded Circular Progress Bar.
  - "Take Daily Photo" floating action button.
  - **Daily Tasks List**: Interactive checkboxes. Confetti or checkmark animations on completion.
  - **Visual Timeline Section**: Horizontal scrolling carousel of past daily photos with their respective AI observations ("Plant Diary").

### 4.5 AI Contextual Chat Interface
- Accessible via a FAB (Floating Action Button) or dedicated tab inside a Plant View.
- Chat interface integrating with `/api/chat`.
- Renders markdown responses smoothly.

---

## 5. Phase 4: Polish, Optimization & Future-Proofing

### 5.1 Caching Strategy & Rate Limiting
- **Redis Integration**: 
  - Cache OpenWeatherMap responses (TTL 1-3 hours).
  - Cache identical Gemini prompt results (based on image hash + plant state) to prevent duplicate API costs.
- **Image Compression**: Compress and resize images on the client side (Canvas API) or FastAPI middleware before sending to Gemini Vision to lower token usage and upload latency.

### 5.2 Gamification
- Add basic streak calculations (derived from `DailyLogs`).
- Display achievement badges on the Dashboard (e.g., "7-Day Streak", "Perfect Garden").

### 5.3 UX & Performance
- Ensure core interaction times are met: 
  - Image Upload/Analysis < 7 seconds.
  - Dashboard load < 2 seconds (using React Query cache).
- Add beginner-friendly tooltips ("Beginner Mode") explaining why certain AI decisions were made.

---

## 6. Full API Route Summary

| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/api/gardens` | List all gardens for authenticated user |
| `POST` | `/api/gardens` | Create a new garden |
| `GET` | `/api/gardens/{id}/plants` | List plants in a specific garden |
| `POST` | `/api/plants/identify` | AI image identification & care profile gen |
| `POST` | `/api/plants` | Add plant to garden |
| `GET` | `/api/plants/{id}` | Get plant details & current health |
| `POST` | `/api/plants/{id}/analyze`| Upload daily photo for Gemini analysis |
| `GET` | `/api/plants/{id}/logs` | Get visual timeline history (Daily logs) |
| `GET` | `/api/plants/{id}/tasks` | Get today's adaptive AI tasks |
| `POST` | `/api/plants/{id}/tasks/{taskId}` | Mark specific task complete |
| `POST` | `/api/chat` | RAG-based AI assistant endpoint |
| `GET` | `/api/weather` | Fetch cached localized weather data |
