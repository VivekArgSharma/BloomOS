from fastapi import APIRouter, Depends, HTTPException

from app.core.auth import CurrentUser, get_current_user
from app.core.config import Settings, get_settings
from app.core.deps import get_store
from app.models.schemas import ChatRequest, ChatResponse
from app.services.gemini import GeminiService


router = APIRouter()

# Teaching Context (Faked RAG)
TEACHING_CONTEXT = """
- Principle: Always explain the 'why' behind care instructions to empower the user.
- Principle: Encourage mindfulness; plant care is a ritual of calmness.
- Fact: Photosynthesis is how plants turn light into life; light is their food, water is just the transport.
- Fact: Most root rot is caused by 'kindness' (overwatering). Soil should usually be dry 1-2 inches down.
- Fact: Yellowing is often a sign of stress—either too much water or lack of nutrients like Nitrogen.
- Fact: Humidity is critical for tropicals; brown tips are often a cry for a misting or a pebble tray.
- Fact: Soil pH affects nutrient availability; most plants prefer slightly acidic soil (pH 6.0-7.0).
- Fact: Companion planting can help deter pests; marigolds are great bodyguards for many plants.
- Fact: Seasonal changes mean light angles change; your plant's favorite spot in summer might be too dark in winter.
"""

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

    # Use recent logs for grounding
    grounding = store.recent_grounding(user.id, payload.plant_id)
    
    llm = GeminiService(settings)
    if llm.enabled:
        prompt = (
            "You are BloomIQ, a calm, intelligent, and teacher-like plant care assistant. "
            "Your goal is not just to give instructions, but to teach the user the language of their plants.\n\n"
            f"Current Plant Context: {plant.model_dump()}\n"
            f"Knowledge Base Grounding: {grounding}\n"
            f"Teaching Principles & Plant Science: {TEACHING_CONTEXT}\n\n"
            f"User Question: {payload.question}\n\n"
            "Respond in a premium, helpful, and slightly cinematic tone. "
            "Address the question directly using the context provided. "
            "If the grounding suggests it, explain the biological 'why'."
        )
        answer = llm.generate_text(prompt)
    else:
        answer = (
            f"BloomIQ here. For your {plant.common_name}, I'm currently in offline mode. "
            "However, remember the golden rule: observe the leaves, feel the soil. "
            "I'll be back online with full intelligence shortly."
        )
        
    return ChatResponse(answer=answer, grounding=grounding)
