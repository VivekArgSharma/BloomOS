from __future__ import annotations

from datetime import date

from app.models.schemas import DailyLog, DailyPlan, Plant, TaskItem, WeatherResponse
from app.services.gemini import GeminiService


TASK_SCHEMA = """
{
  \"tasks\": [
    {
      \"title\": string,
      \"description\": string,
      \"category\": \"water\" | \"monitor\" | \"feed\" | \"sunlight\" | \"photo\"
    }
  ]
}
""".strip()


class PlannerService:
    def __init__(self, gemini: GeminiService) -> None:
        self.gemini = gemini

    def build_plan(self, plant: Plant, weather: WeatherResponse, recent_logs: list[DailyLog]) -> DailyPlan:
        tasks: list[TaskItem]
        if self.gemini.enabled:
            payload = self.gemini.generate_json(
                prompt=(
                    f"Create 3-4 practical daily care tasks for {plant.common_name} ({plant.species_name}). "
                    f"Care profile: {plant.care_profile.model_dump()}. Weather: {weather.model_dump()}. "
                    f"Recent logs: {[log.analysis.model_dump() for log in recent_logs[:3]]}"
                ),
                schema_hint=TASK_SCHEMA,
            )
            tasks = [
                TaskItem(
                    id=f"{plant.id}-{index}",
                    title=item["title"],
                    description=item["description"],
                    category=item.get("category", "monitor"),
                )
                for index, item in enumerate(payload.get("tasks", []), start=1)
            ]
        else:
            tasks = self._fallback_tasks(plant, weather)

        return DailyPlan(
            plant_id=plant.id,
            date=date.today(),
            tasks=tasks,
            weather_snapshot=weather.model_dump(),
            generated_by_ai=self.gemini.enabled,
        )

    def _fallback_tasks(self, plant: Plant, weather: WeatherResponse) -> list[TaskItem]:
        rain_note = "Skip full watering if rain or humidity keeps the soil moist." if weather.rain_chance >= 40 else "Water only if the top layer feels dry."
        tasks = [
            TaskItem(
                id=f"{plant.id}-water",
                title="Check soil moisture",
                description=rain_note,
                category="water",
            ),
            TaskItem(
                id=f"{plant.id}-light",
                title="Review light exposure",
                description=f"Aim for {plant.care_profile.light} light today.",
                category="sunlight",
            ),
            TaskItem(
                id=f"{plant.id}-photo",
                title="Upload a progress photo",
                description="Capture leaves and soil in one frame to improve trend analysis.",
                category="photo",
            ),
        ]
        if plant.recovery_mode:
            tasks.append(
                TaskItem(
                    id=f"{plant.id}-recovery",
                    title="Recovery check",
                    description="Inspect leaf edges, droop, and new growth before changing fertilizer or watering.",
                    category="monitor",
                )
            )
        return tasks
