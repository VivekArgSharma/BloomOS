from __future__ import annotations

from uuid import UUID

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile

from app.core.auth import CurrentUser, get_current_user
from app.core.config import Settings, get_settings
from app.core.deps import get_store, get_supabase_admin_client
from app.models.schemas import DailyLog, DailyPlan, Plant, PlantAnalytics, PlantCreate, PlantDetails, PlantIdentificationResponse, PlantCatalogItem, TaskUpdateResponse
from app.services.analysis import AnalysisService
from app.services.catalog import CatalogService
from app.services.gemini import GeminiService
from app.services.planner import PlannerService
from app.services.storage import StorageService
from app.services.weather import WeatherService


router = APIRouter()


async def _read_image(upload: UploadFile | None, settings: Settings) -> tuple[bytes | None, str | None, str]:
    if upload is None:
        return None, None, ""
    content = await upload.read()
    if len(content) > settings.max_upload_bytes:
        raise HTTPException(status_code=413, detail="Uploaded image is too large")
    return content, upload.content_type or "image/jpeg", upload.filename or "upload.jpg"


@router.get("/catalog", response_model=list[PlantCatalogItem])
def get_catalog(store=Depends(get_store), user: CurrentUser = Depends(get_current_user)) -> list[PlantCatalogItem]:
    return CatalogService(store, GeminiService(get_settings())).list_catalog()


@router.post("/plants/identify", response_model=PlantIdentificationResponse)
async def identify_plant(
    search_hint: str = Form(default=""),
    image: UploadFile | None = File(default=None),
    store=Depends(get_store),
    user: CurrentUser = Depends(get_current_user),
    settings: Settings = Depends(get_settings),
) -> PlantIdentificationResponse:
    image_bytes, mime_type, filename = await _read_image(image, settings)
    hint = search_hint or filename
    return CatalogService(store, GeminiService(settings)).identify(hint, image_bytes=image_bytes, mime_type=mime_type)


@router.post("/plants", response_model=Plant, status_code=201)
async def create_plant(
    payload: PlantCreate,
    store=Depends(get_store),
    user: CurrentUser = Depends(get_current_user),
    settings: Settings = Depends(get_settings),
) -> Plant:
    plant = store.create_plant(user.id, payload)
    garden = store.get_garden(user.id, payload.garden_id)
    weather = await WeatherService(settings).get_weather(garden.city if garden else None)
    plan = PlannerService(GeminiService(settings)).build_plan(plant, weather, recent_logs=[])
    store.upsert_plan(user.id, plan)
    return plant


@router.get("/plants/{plant_id}", response_model=PlantDetails)
def get_plant(plant_id: UUID, store=Depends(get_store), user: CurrentUser = Depends(get_current_user)) -> PlantDetails:
    plant = store.get_plant(user.id, plant_id)
    if plant is None:
        raise HTTPException(status_code=404, detail="Plant not found")
    logs = store.list_logs(user.id, plant_id)
    plan = store.get_plan(user.id, plant_id)
    return PlantDetails(plant=plant, latest_log=logs[0] if logs else None, plan=plan)


@router.post("/plants/{plant_id}/analyze", response_model=DailyLog)
async def analyze_plant(
    plant_id: UUID,
    image: UploadFile = File(...),
    observations: str = Form(default=""),
    store=Depends(get_store),
    user: CurrentUser = Depends(get_current_user),
    settings: Settings = Depends(get_settings),
) -> DailyLog:
    plant = store.get_plant(user.id, plant_id)
    if plant is None:
        raise HTTPException(status_code=404, detail="Plant not found")

    image_bytes, mime_type, filename = await _read_image(image, settings)
    if image_bytes is None or mime_type is None:
        raise HTTPException(status_code=400, detail="Image upload is required")

    photo_url = filename
    if not settings.use_mock_data:
        storage = StorageService(get_supabase_admin_client(), settings)
        photo_url = storage.upload_plant_photo(plant_id, filename, image_bytes, mime_type)
    else:
        photo_url = f"mock://uploads/{filename}"

    analysis = AnalysisService(GeminiService(settings)).analyze_photo(
        plant,
        observations,
        image_bytes=image_bytes,
        mime_type=mime_type,
    )
    log = store.save_analysis(user.id, plant_id, analysis, photo_url=photo_url, observations=observations)
    garden = store.get_garden(user.id, plant.garden_id)
    weather = await WeatherService(settings).get_weather(garden.city if garden else None)
    updated_logs = store.list_logs(user.id, plant_id)
    plan = PlannerService(GeminiService(settings)).build_plan(store.get_plant(user.id, plant_id), weather, updated_logs)  # type: ignore[arg-type]
    store.upsert_plan(user.id, plan)
    return log


@router.get("/plants/{plant_id}/logs", response_model=list[DailyLog])
def get_logs(plant_id: UUID, store=Depends(get_store), user: CurrentUser = Depends(get_current_user)) -> list[DailyLog]:
    if store.get_plant(user.id, plant_id) is None:
        raise HTTPException(status_code=404, detail="Plant not found")
    return store.list_logs(user.id, plant_id)


@router.get("/plants/{plant_id}/tasks", response_model=DailyPlan)
async def get_tasks(
    plant_id: UUID,
    store=Depends(get_store),
    user: CurrentUser = Depends(get_current_user),
    settings: Settings = Depends(get_settings),
) -> DailyPlan:
    plant = store.get_plant(user.id, plant_id)
    if plant is None:
        raise HTTPException(status_code=404, detail="Plant not found")
    plan = store.get_plan(user.id, plant_id)
    if plan is None:
        garden = store.get_garden(user.id, plant.garden_id)
        weather = await WeatherService(settings).get_weather(garden.city if garden else None)
        logs = store.list_logs(user.id, plant_id)
        plan = PlannerService(GeminiService(settings)).build_plan(plant, weather, logs)
        plan = store.upsert_plan(user.id, plan)
    return plan


@router.get("/plants/{plant_id}/analytics", response_model=PlantAnalytics)
def get_plant_analytics(plant_id: UUID, store=Depends(get_store), user: CurrentUser = Depends(get_current_user)) -> PlantAnalytics:
    analytics = store.get_plant_analytics(user.id, plant_id)
    if analytics is None:
        raise HTTPException(status_code=404, detail="Plant not found")
    return analytics


@router.post("/plants/{plant_id}/tasks/{task_id}", response_model=TaskUpdateResponse)
def complete_task(plant_id: UUID, task_id: str, store=Depends(get_store), user: CurrentUser = Depends(get_current_user)) -> TaskUpdateResponse:
    task = store.complete_task(user.id, plant_id, task_id)
    if task is None:
        raise HTTPException(status_code=404, detail="Task not found")
    return TaskUpdateResponse(plant_id=plant_id, task=task, progress_percent=store.progress_percent(user.id, plant_id))
