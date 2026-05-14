from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.api.router import api_router
from app.core.config import get_settings


settings = get_settings()

app = FastAPI(
    title="PlantIQ API",
    version="0.1.0",
    description="AI-powered plant care backend — local Ollama edition.",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        settings.frontend_url,
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://localhost:3000",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.exception_handler(RuntimeError)
async def runtime_error_handler(request, exc: RuntimeError):
    msg = str(exc)
    print(f"RuntimeError: {msg}")
    if "Ollama" in msg or "Cannot connect" in msg:
        return JSONResponse(status_code=503, content={"detail": msg})
    return JSONResponse(status_code=500, content={"detail": msg})


app.include_router(api_router, prefix="/api")


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok", "mode": "mock" if settings.use_mock_data else "supabase"}
