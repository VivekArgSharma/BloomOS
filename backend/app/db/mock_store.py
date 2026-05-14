from __future__ import annotations

from collections import defaultdict
from datetime import date
from typing import Iterable
from uuid import UUID

from app.db.seed_catalog import PLANT_CATALOG
from app.models.schemas import AnalysisResult, DailyLog, DailyPlan, Garden, GardenCreate, Plant, PlantCatalogItem, PlantCreate, TaskItem


class MockStore:
    def __init__(self) -> None:
        self.catalog: list[PlantCatalogItem] = PLANT_CATALOG
        self.gardens: list[Garden] = [
            Garden(name="Balcony Garden", location_type="balcony", city="Bengaluru", health_score=84, plant_count=3),
            Garden(name="Living Room Jungle", location_type="indoor", city="Bengaluru", health_score=79, plant_count=2),
        ]
        self.plants: list[Plant] = []
        self.logs: dict[UUID, list[DailyLog]] = defaultdict(list)
        self.plans: dict[UUID, DailyPlan] = {}
        self._bootstrap_demo_plants()

    def _bootstrap_demo_plants(self) -> None:
        starters = [
            (self.gardens[0].id, "Tulsi"),
            (self.gardens[0].id, "Tomato"),
            (self.gardens[0].id, "Mint"),
            (self.gardens[1].id, "Monstera"),
            (self.gardens[1].id, "Snake Plant"),
        ]
        for garden_id, common_name in starters:
            catalog_item = self.find_catalog_by_name(common_name)
            if catalog_item is None:
                continue
            plant = Plant(
                garden_id=garden_id,
                common_name=catalog_item.common_name,
                species_name=catalog_item.species_name,
                care_profile=catalog_item.care_profile,
                source="catalog",
                current_health_score=8,
            )
            self.plants.append(plant)
            self.plans[plant.id] = self._default_plan(plant.id, common_name)
        self._update_garden_counts()

    def _update_garden_counts(self) -> None:
        for garden in self.gardens:
            related = [plant for plant in self.plants if plant.garden_id == garden.id]
            garden.plant_count = len(related)
            garden.health_score = round(sum((plant.current_health_score * 10) for plant in related) / len(related)) if related else 0

    def _default_plan(self, plant_id: UUID, common_name: str) -> DailyPlan:
        return DailyPlan(
            plant_id=plant_id,
            date=date.today(),
            weather_snapshot={"summary": "Warm and partly cloudy", "temperature_c": 27, "humidity": 58, "rain_chance": 15},
            tasks=[
                TaskItem(id=f"{plant_id}-water", title=f"Check {common_name} moisture", description="Insert a finger 2cm into the soil before watering.", category="water"),
                TaskItem(id=f"{plant_id}-sun", title="Rotate for even light", description="Turn the pot slightly to balance growth toward the light source.", category="sunlight"),
                TaskItem(id=f"{plant_id}-photo", title="Upload a progress photo", description="Capture a clear leaf and soil view for trend tracking.", category="photo"),
            ],
        )

    def list_catalog(self) -> list[PlantCatalogItem]:
        return self.catalog

    def find_catalog_by_name(self, name: str) -> PlantCatalogItem | None:
        normalized = name.strip().lower()
        for item in self.catalog:
            aliases = {item.common_name.lower(), item.species_name.lower()}
            if normalized in aliases:
                return item
        return None

    def search_catalog(self, query: str) -> PlantCatalogItem | None:
        normalized = query.strip().lower()
        for item in self.catalog:
            haystack = " ".join([item.common_name, item.species_name, *item.tags]).lower()
            if normalized and normalized in haystack:
                return item
        return None

    def list_gardens(self) -> list[Garden]:
        self._update_garden_counts()
        return self.gardens

    def create_garden(self, payload: GardenCreate) -> Garden:
        garden = Garden(**payload.model_dump())
        self.gardens.append(garden)
        return garden

    def list_garden_plants(self, garden_id: UUID) -> list[Plant]:
        return [plant for plant in self.plants if plant.garden_id == garden_id]

    def create_plant(self, payload: PlantCreate) -> Plant:
        plant = Plant(**payload.model_dump())
        self.plants.append(plant)
        self.plans[plant.id] = self._default_plan(plant.id, plant.common_name)
        self._update_garden_counts()
        return plant

    def get_plant(self, plant_id: UUID) -> Plant | None:
        for plant in self.plants:
            if plant.id == plant_id:
                return plant
        return None

    def save_analysis(self, plant_id: UUID, analysis: AnalysisResult, photo_url: str, observations: str) -> DailyLog:
        log = DailyLog(plant_id=plant_id, photo_url=photo_url, observations=observations, analysis=analysis)
        self.logs[plant_id].append(log)
        plant = self.get_plant(plant_id)
        if plant:
            plant.current_health_score = analysis.health_score
            plant.recovery_mode = analysis.health_score < 5
            self.plans[plant_id] = self._adaptive_plan(plant)
        self._update_garden_counts()
        return log

    def _adaptive_plan(self, plant: Plant) -> DailyPlan:
        extra_monitoring = plant.current_health_score < 5
        tasks = [
            TaskItem(id=f"{plant.id}-water", title="Review soil moisture", description="Only water if the top layer feels dry enough for this species.", category="water"),
            TaskItem(id=f"{plant.id}-monitor", title="Inspect leaves for stress", description="Look for curling, spotting, droop, or edge crisping.", category="monitor"),
            TaskItem(id=f"{plant.id}-photo", title="Capture today's plant photo", description="Keep the same framing so changes are easy to compare.", category="photo"),
        ]
        if extra_monitoring:
            tasks.append(TaskItem(id=f"{plant.id}-recovery", title="Begin recovery routine", description="Move to bright filtered light and avoid fertilizer until new stable growth appears.", category="monitor"))
        return DailyPlan(
            plant_id=plant.id,
            date=date.today(),
            weather_snapshot={"summary": "Humid afternoon with light breeze", "temperature_c": 28, "humidity": 64, "rain_chance": 30},
            tasks=tasks,
        )

    def list_logs(self, plant_id: UUID) -> list[DailyLog]:
        return list(reversed(self.logs.get(plant_id, [])))

    def get_plan(self, plant_id: UUID) -> DailyPlan | None:
        return self.plans.get(plant_id)

    def complete_task(self, plant_id: UUID, task_id: str) -> TaskItem | None:
        plan = self.plans.get(plant_id)
        if plan is None:
            return None
        for task in plan.tasks:
            if task.id == task_id:
                task.completed = True
                return task
        return None

    def progress_percent(self, plant_id: UUID) -> int:
        plan = self.plans.get(plant_id)
        if plan is None or not plan.tasks:
            return 0
        completed = sum(1 for task in plan.tasks if task.completed)
        return round((completed / len(plan.tasks)) * 100)

    def recent_grounding(self, plant_id: UUID) -> Iterable[str]:
        plant = self.get_plant(plant_id)
        if not plant:
            return []
        snippets = [
            f"{plant.common_name} usually prefers {plant.care_profile.light} light.",
            f"Typical watering interval is every {plant.care_profile.water_interval_days} days.",
        ]
        latest_log = self.logs.get(plant_id, [])[-1] if self.logs.get(plant_id) else None
        if latest_log:
            snippets.append(f"Latest analysis score: {latest_log.analysis.health_score}/10 with issues: {', '.join(latest_log.analysis.visible_issues) or 'none' }.")
        return snippets
