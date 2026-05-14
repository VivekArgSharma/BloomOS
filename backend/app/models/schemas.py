from __future__ import annotations

from datetime import date as dt_date, datetime
from typing import Any, Literal
from uuid import UUID, uuid4

from pydantic import BaseModel, Field


class GardenBase(BaseModel):
    name: str
    location_type: str
    city: str | None = None
    latitude: float | None = None
    longitude: float | None = None


class GardenCreate(GardenBase):
    user_id: str = "demo-user"


class Garden(GardenBase):
    id: UUID = Field(default_factory=uuid4)
    user_id: str = "demo-user"
    created_at: datetime = Field(default_factory=datetime.utcnow)
    health_score: int = 82
    plant_count: int = 0


class CareProfile(BaseModel):
    water_interval_days: int
    light: str
    humidity: str
    fertilizer: str
    soil: str
    notes: list[str] = Field(default_factory=list)


class PlantCatalogItem(BaseModel):
    id: UUID = Field(default_factory=uuid4)
    common_name: str
    species_name: str
    difficulty: Literal["easy", "moderate", "advanced"]
    tags: list[str] = Field(default_factory=list)
    care_profile: CareProfile


class PlantCreate(BaseModel):
    garden_id: UUID
    common_name: str
    species_name: str
    source: Literal["catalog", "image"] = "catalog"
    care_profile: CareProfile


class Plant(BaseModel):
    id: UUID = Field(default_factory=uuid4)
    garden_id: UUID
    common_name: str
    species_name: str
    care_profile: CareProfile
    source: Literal["catalog", "image"] = "catalog"
    current_health_score: int = 8
    recovery_mode: bool = False
    added_at: datetime = Field(default_factory=datetime.utcnow)


class PlantIdentificationResponse(BaseModel):
    matched_catalog: bool
    confidence: float
    plant: PlantCatalogItem
    rationale: str


class AnalysisResult(BaseModel):
    health_score: int
    visible_issues: list[str]
    soil_moisture: str
    recommended_action: str
    flag_urgent: bool
    diary_entry: str


class DailyLog(BaseModel):
    id: UUID = Field(default_factory=uuid4)
    plant_id: UUID
    photo_url: str
    observations: str
    analysis: AnalysisResult
    created_at: datetime = Field(default_factory=datetime.utcnow)


class TaskItem(BaseModel):
    id: str
    title: str
    description: str
    category: Literal["water", "monitor", "feed", "sunlight", "photo"]
    completed: bool = False


class DailyPlan(BaseModel):
    id: UUID = Field(default_factory=uuid4)
    plant_id: UUID
    date: dt_date = Field(default_factory=dt_date.today)
    tasks: list[TaskItem]
    weather_snapshot: dict[str, Any]
    generated_by_ai: bool = True


class TaskUpdateResponse(BaseModel):
    plant_id: UUID
    task: TaskItem
    progress_percent: int


class PlantDetails(BaseModel):
    plant: Plant
    latest_log: DailyLog | None = None
    plan: DailyPlan | None = None


class ChatRequest(BaseModel):
    plant_id: UUID
    question: str


class ChatResponse(BaseModel):
    answer: str
    grounding: list[str]


class WeatherResponse(BaseModel):
    city: str
    summary: str
    temperature_c: int
    humidity: int
    rain_chance: int
