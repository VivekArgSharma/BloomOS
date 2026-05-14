from __future__ import annotations

from collections import defaultdict
from datetime import date, datetime, timedelta
from typing import Iterable
from uuid import UUID

from app.db.seed_catalog import PLANT_CATALOG
from app.models.schemas import (
    AnalysisResult,
    CompletionPoint,
    DailyLog,
    DailyPlan,
    Garden,
    GardenAnalytics,
    GardenCreate,
    GardenPlantSnapshot,
    HealthPoint,
    IssueCount,
    Plant,
    PlantAnalytics,
    PlantCatalogItem,
    PlantCreate,
    TaskItem,
)


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
        self.completion_history: dict[UUID, list[CompletionPoint]] = defaultdict(list)
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
            self._seed_analytics_history(plant)
        self._update_garden_counts()

    def _seed_analytics_history(self, plant: Plant) -> None:
        baseline_map = {
            "Tulsi": [6, 7, 7, 8, 8, 8, 9],
            "Tomato": [5, 6, 6, 7, 7, 8, 8],
            "Mint": [7, 7, 8, 8, 8, 9, 9],
            "Monstera": [6, 7, 7, 7, 8, 8, 8],
            "Snake Plant": [8, 8, 8, 8, 8, 9, 9],
        }
        scores = baseline_map.get(plant.common_name, [6, 6, 7, 7, 7, 8, 8])
        issue_map = {
            9: ["healthy foliage"],
            8: ["healthy foliage"],
            7: ["minor dryness"],
            6: ["slight droop"],
            5: ["yellowing", "mild wilting"],
        }
        now = datetime.utcnow()
        for days_ago, score in enumerate(reversed(scores), start=1):
            created_at = now - timedelta(days=days_ago)
            log = DailyLog(
                plant_id=plant.id,
                photo_url=f"mock://history/{plant.common_name.lower().replace(' ', '-')}-{days_ago}.jpg",
                observations=f"Historical check-in for {plant.common_name}",
                analysis=AnalysisResult(
                    health_score=score,
                    visible_issues=issue_map.get(score, ["healthy foliage"]),
                    soil_moisture="adequate" if score >= 7 else "slightly dry",
                    recommended_action="Keep conditions stable and continue observing leaf posture.",
                    flag_urgent=score < 5,
                    diary_entry=f"Day snapshot: {plant.common_name} tracked at {score}/10 health.",
                ),
                created_at=created_at,
            )
            self.logs[plant.id].append(log)
        plant.current_health_score = scores[-1]
        plant.recovery_mode = scores[-1] < 5
        self.completion_history[plant.id] = [
            CompletionPoint(label="Mon", completed=2, total=3, rate=67),
            CompletionPoint(label="Tue", completed=3, total=3, rate=100),
            CompletionPoint(label="Wed", completed=2, total=3, rate=67),
            CompletionPoint(label="Thu", completed=3, total=3, rate=100),
            CompletionPoint(label="Fri", completed=2, total=3, rate=67),
            CompletionPoint(label="Sat", completed=3, total=3, rate=100),
            CompletionPoint(label="Sun", completed=3, total=3, rate=100),
        ]

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

    def list_gardens(self, user_id: str | None = None) -> list[Garden]:
        self._update_garden_counts()
        return self.gardens

    def get_garden(self, user_id: str | None, garden_id: UUID) -> Garden | None:
        self._update_garden_counts()
        return next((garden for garden in self.gardens if garden.id == garden_id), None)

    def create_garden(self, user_id: str | None, payload: GardenCreate) -> Garden:
        garden = Garden(**payload.model_dump())
        self.gardens.append(garden)
        return garden

    def list_garden_plants(self, user_id: str | None, garden_id: UUID) -> list[Plant]:
        return [plant for plant in self.plants if plant.garden_id == garden_id]

    def create_plant(self, user_id: str | None, payload: PlantCreate) -> Plant:
        plant = Plant(**payload.model_dump())
        self.plants.append(plant)
        self.plans[plant.id] = self._default_plan(plant.id, plant.common_name)
        self._seed_analytics_history(plant)
        self._update_garden_counts()
        return plant

    def get_plant(self, user_id: str | None, plant_id: UUID) -> Plant | None:
        for plant in self.plants:
            if plant.id == plant_id:
                return plant
        return None

    def save_analysis(self, user_id: str | None, plant_id: UUID, analysis: AnalysisResult, photo_url: str, observations: str) -> DailyLog:
        log = DailyLog(plant_id=plant_id, photo_url=photo_url, observations=observations, analysis=analysis)
        self.logs[plant_id].append(log)
        plant = self.get_plant(user_id, plant_id)
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

    def list_logs(self, user_id: str | None, plant_id: UUID) -> list[DailyLog]:
        return list(reversed(self.logs.get(plant_id, [])))

    def get_plan(self, user_id: str | None, plant_id: UUID) -> DailyPlan | None:
        return self.plans.get(plant_id)

    def upsert_plan(self, user_id: str | None, plan: DailyPlan) -> DailyPlan:
        self.plans[plan.plant_id] = plan
        return plan

    def get_recent_plans(self, user_id: str | None, plant_id: UUID, limit: int = 7) -> list[DailyPlan]:
        plan = self.plans.get(plant_id)
        return [plan] if plan else []

    def complete_task(self, user_id: str | None, plant_id: UUID, task_id: str) -> TaskItem | None:
        plan = self.plans.get(plant_id)
        if plan is None:
            return None
        for task in plan.tasks:
            if task.id == task_id:
                task.completed = True
                self._record_task_completion(plant_id, plan)
                return task
        return None

    def _record_task_completion(self, plant_id: UUID, plan: DailyPlan) -> None:
        completed = sum(1 for task in plan.tasks if task.completed)
        total = len(plan.tasks)
        latest = CompletionPoint(label=date.today().strftime("%a"), completed=completed, total=total, rate=round((completed / total) * 100) if total else 0)
        history = self.completion_history[plant_id]
        if history and history[-1].label == latest.label:
            history[-1] = latest
        else:
            history.append(latest)
            if len(history) > 7:
                del history[0]

    def progress_percent(self, user_id: str | None, plant_id: UUID) -> int:
        plan = self.plans.get(plant_id)
        if plan is None or not plan.tasks:
            return 0
        completed = sum(1 for task in plan.tasks if task.completed)
        return round((completed / len(plan.tasks)) * 100)

    def recent_grounding(self, user_id: str | None, plant_id: UUID) -> Iterable[str]:
        plant = self.get_plant(user_id, plant_id)
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

    def get_plant_analytics(self, user_id: str | None, plant_id: UUID) -> PlantAnalytics | None:
        plant = self.get_plant(user_id, plant_id)
        if plant is None:
            return None
        raw_logs = self.logs.get(plant_id, [])
        if not raw_logs:
            return PlantAnalytics(
                plant_id=plant_id,
                current_health=plant.current_health_score,
                average_health=plant.current_health_score,
                health_delta=0,
                streak_days=0,
                task_completion_rate=0,
                watering_consistency=0,
                issue_breakdown=[],
                health_history=[],
                completion_history=[],
                insight="No analytics yet. Start daily photo logging to unlock plant trends.",
            )

        recent_logs = raw_logs[-7:]
        scores = [log.analysis.health_score for log in recent_logs]
        issue_counts: dict[str, int] = defaultdict(int)
        for log in raw_logs:
            for issue in log.analysis.visible_issues:
                issue_counts[issue] += 1

        completion_history = self.completion_history.get(plant_id, [])[-7:]
        average_completion = round(sum(item.rate for item in completion_history) / len(completion_history)) if completion_history else 0
        streak_days = sum(1 for item in reversed(completion_history) if item.rate >= 67)
        watering_consistency = max(35, min(100, average_completion - 5 + plant.care_profile.water_interval_days * 2))
        health_delta = scores[-1] - scores[0]
        direction = "improving" if health_delta > 0 else "holding steady" if health_delta == 0 else "slipping"

        return PlantAnalytics(
            plant_id=plant_id,
            current_health=plant.current_health_score,
            average_health=round(sum(scores) / len(scores)),
            health_delta=health_delta,
            streak_days=streak_days,
            task_completion_rate=average_completion,
            watering_consistency=watering_consistency,
            issue_breakdown=[IssueCount(issue=issue, count=count) for issue, count in sorted(issue_counts.items(), key=lambda item: item[1], reverse=True)],
            health_history=[HealthPoint(label=log.created_at.strftime("%a"), score=log.analysis.health_score) for log in recent_logs],
            completion_history=completion_history,
            insight=f"{plant.common_name} is {direction}; keep the next few days consistent to stabilize the trend.",
        )

    def get_garden_analytics(self, user_id: str | None, garden_id: UUID) -> GardenAnalytics | None:
        garden = next((item for item in self.gardens if item.id == garden_id), None)
        if garden is None:
            return None
        plants = self.list_garden_plants(user_id, garden_id)
        if not plants:
            return GardenAnalytics(
                garden_id=garden_id,
                overall_health=0,
                average_completion_rate=0,
                plants_in_recovery=0,
                issue_breakdown=[],
                health_history=[],
                plant_snapshots=[],
                recommended_focus="Add your first plant to begin garden-level analytics.",
            )

        analytics = [self.get_plant_analytics(user_id, plant.id) for plant in plants]
        valid_analytics = [item for item in analytics if item is not None]
        history_len = min((len(item.health_history) for item in valid_analytics), default=0)
        garden_history: list[HealthPoint] = []
        for index in range(history_len):
            label = valid_analytics[0].health_history[index].label
            avg_score = round(sum(item.health_history[index].score for item in valid_analytics) / len(valid_analytics))
            garden_history.append(HealthPoint(label=label, score=avg_score))

        issue_counts: dict[str, int] = defaultdict(int)
        for item in valid_analytics:
            for issue in item.issue_breakdown:
                issue_counts[issue.issue] += issue.count

        healthiest = max(plants, key=lambda item: item.current_health_score)
        needs_attention = min(plants, key=lambda item: item.current_health_score)
        completion_by_plant: dict[UUID, int] = {}
        for item in valid_analytics:
            completion_by_plant[item.plant_id] = item.task_completion_rate
        snapshots = [
            GardenPlantSnapshot(
                plant_id=plant.id,
                common_name=plant.common_name,
                health_score=plant.current_health_score,
                completion_rate=completion_by_plant.get(plant.id, 0),
                recovery_mode=plant.recovery_mode,
            )
            for plant in plants
        ]

        avg_completion = round(sum(item.completion_rate for item in snapshots) / len(snapshots))
        plants_in_recovery = sum(1 for plant in plants if plant.recovery_mode)
        return GardenAnalytics(
            garden_id=garden_id,
            overall_health=round(sum(plant.current_health_score for plant in plants) / len(plants) * 10),
            average_completion_rate=avg_completion,
            plants_in_recovery=plants_in_recovery,
            healthiest_plant=healthiest.common_name,
            needs_attention_plant=needs_attention.common_name,
            issue_breakdown=[IssueCount(issue=issue, count=count) for issue, count in sorted(issue_counts.items(), key=lambda item: item[1], reverse=True)],
            health_history=garden_history,
            plant_snapshots=snapshots,
            recommended_focus=f"Focus on {needs_attention.common_name} first, then keep task completion above {max(80, avg_completion)}% across the garden.",
        )
