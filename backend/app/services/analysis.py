from __future__ import annotations

from app.models.schemas import AnalysisResult, Plant
from app.services.gemini import GeminiService


ANALYSIS_SCHEMA = """
{
  \"health_score\": number,
  \"visible_issues\": string[],
  \"soil_moisture\": string,
  \"recommended_action\": string,
  \"flag_urgent\": boolean,
  \"diary_entry\": string
}
""".strip()


class AnalysisService:
    def __init__(self, gemini: GeminiService) -> None:
        self.gemini = gemini

    def analyze_photo(
        self,
        plant: Plant,
        observations: str,
        image_bytes: bytes | None = None,
        mime_type: str | None = None,
    ) -> AnalysisResult:
        if self.gemini.enabled and image_bytes is not None and mime_type is not None:
            payload = self.gemini.generate_json(
                prompt=(
                    f"Analyze the current health of this {plant.common_name} ({plant.species_name}). "
                    f"Base care profile: {plant.care_profile.model_dump()}. User observations: {observations or 'none'}"
                ),
                schema_hint=ANALYSIS_SCHEMA,
                image_bytes=image_bytes,
                mime_type=mime_type,
            )
            return AnalysisResult(**payload)

        if "yellow" in observations.lower() or "droop" in observations.lower():
            return AnalysisResult(
                health_score=5,
                visible_issues=["minor yellowing", "mild wilting"],
                soil_moisture="slightly dry",
                recommended_action="Increase monitoring frequency and verify whether the root zone is drying too quickly.",
                flag_urgent=False,
                diary_entry=f"{plant.common_name} shows early stress today with visible yellowing and slight droop.",
            )

        return AnalysisResult(
            health_score=8,
            visible_issues=["healthy foliage"],
            soil_moisture="adequate",
            recommended_action="Continue the current routine and upload another photo tomorrow for trend tracking.",
            flag_urgent=False,
            diary_entry=f"{plant.common_name} looks stable today with no major stress indicators.",
        )
