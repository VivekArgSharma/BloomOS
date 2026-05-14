from __future__ import annotations

from random import randint

from app.models.schemas import AnalysisResult, Plant


class AnalysisService:
    def analyze_photo(self, plant: Plant, observations: str) -> AnalysisResult:
        if "yellow" in observations.lower() or "droop" in observations.lower():
            health_score = 5
            issues = ["minor yellowing", "mild wilting"]
            moisture = "slightly dry"
            action = "Increase observation frequency and check if the root zone is drying too quickly."
            urgent = False
            diary = f"{plant.common_name} shows mild stress today. Monitor leaf color and keep watering intervals consistent."
        else:
            health_score = randint(7, 9)
            issues = ["healthy foliage"]
            moisture = "adequate"
            action = "Continue the current care routine and upload another photo tomorrow."
            urgent = False
            diary = f"{plant.common_name} looks stable today with no major stress indicators."
        return AnalysisResult(
            health_score=health_score,
            visible_issues=issues,
            soil_moisture=moisture,
            recommended_action=action,
            flag_urgent=urgent,
            diary_entry=diary,
        )
