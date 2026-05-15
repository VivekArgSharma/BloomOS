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
    health_score: int = Field(default=82, ge=0, le=100)
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
    current_health_score: int = Field(default=8, ge=1, le=10)
    recovery_mode: bool = False
    added_at: datetime = Field(default_factory=datetime.utcnow)


class PlantIdentificationResponse(BaseModel):
    matched_catalog: bool
    confidence: float
    plant: PlantCatalogItem
    rationale: str


class AnalysisResult(BaseModel):
    health_score: int = Field(ge=1, le=10)
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


class HealthPoint(BaseModel):
    label: str
    score: int = Field(ge=1, le=10)


class CompletionPoint(BaseModel):
    label: str
    completed: int
    total: int
    rate: int


class IssueCount(BaseModel):
    issue: str
    count: int


class PlantAnalytics(BaseModel):
    plant_id: UUID
    current_health: int
    average_health: int
    health_delta: int
    streak_days: int
    task_completion_rate: int
    watering_consistency: int
    issue_breakdown: list[IssueCount]
    health_history: list[HealthPoint]
    completion_history: list[CompletionPoint]
    insight: str


class GardenPlantSnapshot(BaseModel):
    plant_id: UUID
    common_name: str
    health_score: int = Field(ge=1, le=10)
    completion_rate: int = Field(ge=0, le=100)
    recovery_mode: bool


class GardenAnalytics(BaseModel):
    garden_id: UUID
    overall_health: int
    average_completion_rate: int
    plants_in_recovery: int
    healthiest_plant: str | None = None
    needs_attention_plant: str | None = None
    issue_breakdown: list[IssueCount]
    health_history: list[HealthPoint]
    plant_snapshots: list[GardenPlantSnapshot]
    recommended_focus: str


class CompatibilityCheck(BaseModel):
    compatible: bool
    confidence: int
    issues: list[str]
    recommendations: list[str]
    light_compatibility: dict[str, Any]
    humidity_compatibility: dict[str, Any]


class Badge(BaseModel):
    id: str
    name: str
    description: str
    icon: str
    unlocked: bool


class UserBadges(BaseModel):
    badges: list[Badge]
    total_unlocked: int
    total_available: int


class UserStats(BaseModel):
    garden_count: int
    plant_count: int
    current_streak: int
    longest_streak: int
    total_tasks_completed: int
    total_photos_uploaded: int
    recovery_mode_exits: int
    chat_questions_asked: int
    weather_decisions: int
    plants_at_health_90_plus: int


class AnalysisPreview(BaseModel):
    health_score: int = Field(ge=1, le=10)
    summary: str
    issues: list[str]
    is_urgent: bool


class CommunityProfile(BaseModel):
    id: UUID
    username: str
    display_name: str
    avatar_url: str | None = None
    bio: str | None = None


class CommunityPostCreate(BaseModel):
    body: str = Field(min_length=1, max_length=2000)
    image_url: str | None = None


class CommunityCommentCreate(BaseModel):
    body: str = Field(min_length=1, max_length=1000)


class CommunityPostUpdate(BaseModel):
    body: str = Field(min_length=1, max_length=2000)
    image_url: str | None = None


class CommunityCommentUpdate(BaseModel):
    body: str = Field(min_length=1, max_length=1000)


class CommunityComment(BaseModel):
    id: UUID = Field(default_factory=uuid4)
    post_id: UUID
    author: CommunityProfile
    body: str
    created_at: datetime = Field(default_factory=datetime.utcnow)
    is_owner: bool = False
    updated_at: datetime | None = None


class CommunityPost(BaseModel):
    id: UUID = Field(default_factory=uuid4)
    author: CommunityProfile
    body: str
    image_url: str | None = None
    like_count: int = 0
    comment_count: int = 0
    viewer_has_liked: bool = False
    created_at: datetime = Field(default_factory=datetime.utcnow)
    is_owner: bool = False
    updated_at: datetime | None = None


class CommunityFeedResponse(BaseModel):
    posts: list[CommunityPost]
    next_offset: int | None = None


class CommunityProfileUpdate(BaseModel):
    username: str | None = Field(default=None, min_length=3, max_length=30)
    display_name: str | None = Field(default=None, min_length=1, max_length=80)
    avatar_url: str | None = Field(default=None, max_length=500)
    bio: str | None = Field(default=None, max_length=240)


class CommunityLikeResponse(BaseModel):
    post_id: UUID
    like_count: int
    viewer_has_liked: bool


class CommunityProfilePage(BaseModel):
    profile: CommunityProfile
    posts: list[CommunityPost]
    next_offset: int | None = None
