from app.models.schemas import DailyPlan, Plant


class PlannerService:
    def summarize(self, plant: Plant, plan: DailyPlan | None) -> str:
        if plan is None:
            return f"No plan generated yet for {plant.common_name}."
        pending = [task.title for task in plan.tasks if not task.completed]
        if not pending:
            return f"All tasks for {plant.common_name} are complete today."
        return f"Next best actions for {plant.common_name}: {', '.join(pending[:3])}."
