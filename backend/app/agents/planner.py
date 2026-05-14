from app.models.schemas import DailyPlan, Plant


def build_daily_plan_prompt(plant: Plant, weather: dict, recent_events: list[str]) -> str:
    return (
        f"Generate tasks for {plant.common_name} ({plant.species_name}). "
        f"Weather: {weather}. Recent events: {recent_events}. "
        f"Base watering interval: every {plant.care_profile.water_interval_days} days."
    )


def explain_plan(plan: DailyPlan | None) -> str:
    if plan is None:
        return "Planner has not generated a daily plan yet."
    return "; ".join(task.title for task in plan.tasks)
