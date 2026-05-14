from fastapi import APIRouter, Depends, HTTPException

from app.core.auth import CurrentUser, get_current_user
from app.core.config import Settings, get_settings
from app.core.deps import get_store
from app.models.schemas import ChatRequest, ChatResponse
from app.services.gemini import GeminiService
from app.services.rag import RagService


router = APIRouter()


@router.post("/chat", response_model=ChatResponse)
def chat(
    payload: ChatRequest,
    store=Depends(get_store),
    user: CurrentUser = Depends(get_current_user),
    settings: Settings = Depends(get_settings),
) -> ChatResponse:
    plant = store.get_plant(user.id, payload.plant_id)
    if plant is None:
        raise HTTPException(status_code=404, detail="Plant not found")

    rag = RagService(settings)
    grounding = [*store.recent_grounding(user.id, payload.plant_id), *rag.grounding(payload.question)]
    if GeminiService(settings).enabled:
        prompt = (
            f"You are PlantIQ, a practical plant-care assistant. Plant context: {plant.model_dump()}. "
            f"Grounding facts: {grounding}. User question: {payload.question}. "
            "Answer briefly, concretely, and avoid unsupported claims."
        )
        answer = GeminiService(settings).generate_text(prompt)
    else:
        answer = (
            f"For {plant.common_name}, start with the latest health trend, moisture check, and light consistency. "
            f"Question received: {payload.question}"
        )
    return ChatResponse(answer=answer, grounding=grounding)
