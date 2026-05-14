from fastapi import APIRouter, Depends, HTTPException

from app.core.deps import get_store
from app.db.mock_store import MockStore
from app.models.schemas import ChatRequest, ChatResponse
from app.services.rag import RagService


router = APIRouter()


@router.post("/chat", response_model=ChatResponse)
def chat(payload: ChatRequest, store: MockStore = Depends(get_store)) -> ChatResponse:
    plant = store.get_plant(payload.plant_id)
    if plant is None:
        raise HTTPException(status_code=404, detail="Plant not found")
    rag = RagService()
    grounding = [*store.recent_grounding(payload.plant_id), *rag.grounding(payload.question)]
    answer = (
        f"Based on {plant.common_name}'s current profile, start with light/moisture consistency and review the latest analysis. "
        f"Question received: {payload.question}"
    )
    return ChatResponse(answer=answer, grounding=grounding)
