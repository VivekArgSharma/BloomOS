from uuid import UUID

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile

from app.core.auth import CurrentUser, get_current_user
from app.core.config import Settings, get_settings
from app.core.deps import get_store
from app.models.schemas import AnalysisPreview
from app.services.analysis import get_analysis_service


router = APIRouter()


@router.post("/plants/{plant_id}/preview-analysis", response_model=AnalysisPreview)
async def preview_analysis(
    plant_id: UUID,
    observations: str = Form(default=""),
    image: UploadFile = File(...),
    store=Depends(get_store),
    user: CurrentUser = Depends(get_current_user),
    settings: Settings = Depends(get_settings),
) -> AnalysisPreview:
    """Preview analysis without saving - generates quick AI summary."""
    plant = store.get_plant(user.id, plant_id)
    if plant is None:
        raise HTTPException(status_code=404, detail="Plant not found")
    
    image_bytes = await image.read()
    if len(image_bytes) > settings.max_upload_bytes:
        raise HTTPException(status_code=413, detail="Image too large")
    
    analysis_service = get_analysis_service(settings)
    result = analysis_service.analyze_photo(
        plant,
        observations,
        image_bytes=image_bytes,
        mime_type=image.content_type or "image/jpeg",
    )
    
    return AnalysisPreview(
        health_score=result.health_score,
        summary=result.diary_entry,
        issues=result.visible_issues,
        is_urgent=result.flag_urgent,
    )