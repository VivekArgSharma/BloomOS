from uuid import UUID

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile

from app.core.deps import get_store
from app.db.mock_store import MockStore
from app.models.schemas import DailyLog, DailyPlan, Plant, PlantCreate, PlantDetails, PlantIdentificationResponse, PlantCatalogItem, TaskUpdateResponse
from app.services.analysis import AnalysisService
from app.services.catalog import CatalogService


router = APIRouter()


@router.get("/catalog", response_model=list[PlantCatalogItem])
def get_catalog(store: MockStore = Depends(get_store)) -> list[PlantCatalogItem]:
    return CatalogService(store).list_catalog()


@router.post("/plants/identify", response_model=PlantIdentificationResponse)
async def identify_plant(
    search_hint: str = Form(default=""),
    image: UploadFile | None = File(default=None),
    store: MockStore = Depends(get_store),
) -> PlantIdentificationResponse:
    hint = search_hint or (image.filename if image else "")
    return CatalogService(store).identify(hint)


@router.post("/plants", response_model=Plant, status_code=201)
def create_plant(payload: PlantCreate, store: MockStore = Depends(get_store)) -> Plant:
    return store.create_plant(payload)


@router.get("/plants/{plant_id}", response_model=PlantDetails)
def get_plant(plant_id: UUID, store: MockStore = Depends(get_store)) -> PlantDetails:
    plant = store.get_plant(plant_id)
    if plant is None:
        raise HTTPException(status_code=404, detail="Plant not found")
    logs = store.list_logs(plant_id)
    plan = store.get_plan(plant_id)
    return PlantDetails(plant=plant, latest_log=logs[0] if logs else None, plan=plan)


@router.post("/plants/{plant_id}/analyze", response_model=DailyLog)
async def analyze_plant(
    plant_id: UUID,
    image: UploadFile | None = File(default=None),
    observations: str = Form(default=""),
    store: MockStore = Depends(get_store),
) -> DailyLog:
    plant = store.get_plant(plant_id)
    if plant is None:
        raise HTTPException(status_code=404, detail="Plant not found")
    photo_url = f"mock://uploads/{image.filename}" if image else "mock://uploads/manual-entry.jpg"
    analysis = AnalysisService().analyze_photo(plant, observations)
    return store.save_analysis(plant_id, analysis, photo_url=photo_url, observations=observations)


@router.get("/plants/{plant_id}/logs", response_model=list[DailyLog])
def get_logs(plant_id: UUID, store: MockStore = Depends(get_store)) -> list[DailyLog]:
    return store.list_logs(plant_id)


@router.get("/plants/{plant_id}/tasks", response_model=DailyPlan)
def get_tasks(plant_id: UUID, store: MockStore = Depends(get_store)) -> DailyPlan:
    plan = store.get_plan(plant_id)
    if plan is None:
        raise HTTPException(status_code=404, detail="Daily plan not found")
    return plan


@router.post("/plants/{plant_id}/tasks/{task_id}", response_model=TaskUpdateResponse)
def complete_task(plant_id: UUID, task_id: str, store: MockStore = Depends(get_store)) -> TaskUpdateResponse:
    task = store.complete_task(plant_id, task_id)
    if task is None:
        raise HTTPException(status_code=404, detail="Task not found")
    return TaskUpdateResponse(plant_id=plant_id, task=task, progress_percent=store.progress_percent(plant_id))
