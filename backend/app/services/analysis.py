from __future__ import annotations

from app.core.config import Settings
from app.models.schemas import AnalysisResult, Plant
from app.services.gemini import GeminiService
from app.services.plantid import PlantIdService


ANALYSIS_SCHEMA = """
{
  "health_score": number,
  "visible_issues": string[],
  "soil_moisture": string,
  "recommended_action": string,
  "flag_urgent": boolean,
  "diary_entry": string
}
""".strip()


class AnalysisService:
    def __init__(self, gemini: GeminiService, plantid: PlantIdService) -> None:
        self.gemini = gemini
        self.plantid = plantid

    def analyze_photo(
        self,
        plant: Plant,
        observations: str,
        image_bytes: bytes | None = None,
        mime_type: str | None = None,
    ) -> AnalysisResult:
        # Use Plant.id for health analysis if available
        if self.plantid.enabled and image_bytes is not None:
            health_result = self.plantid.analyze_health(image_bytes)
            if health_result:
                return self._convert_plantid_result(health_result, plant, observations)

        # Fallback to Gemini/OpenRouter analysis
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

        # Last resort - rule-based on observations
        return self._rule_based_analysis(plant, observations)

    def _convert_plantid_result(
        self, 
        health_result: dict, 
        plant: Plant,
        observations: str
    ) -> AnalysisResult:
        """Convert Plant.id result to AnalysisResult format."""
        health_score = health_result.get("health_score", 7)
        health_status = health_result.get("health_status", "unknown")
        diseases = health_result.get("diseases", [])
        recommendations = health_result.get("recommendations", [])
        is_urgent = health_result.get("is_urgent", False)
        visible_issues = health_result.get("visible_issues", [])
        
        # Add disease names to visible issues
        for disease in diseases:
            disease_name = disease.get("name", "")
            if disease_name:
                visible_issues.append(disease_name)
        
        # Generate diary entry
        if health_status == "healthy":
            diary = f"{plant.common_name} looks healthy today. No disease symptoms detected."
        elif health_status == "diseased":
            disease_names = ", ".join([d.get("name", "unknown") for d in diseases])
            diary = f"{plant.common_name} shows signs of disease: {disease_names}. Follow treatment recommendations."
        elif health_status == "dead":
            diary = f"{plant.common_name} appears to be dead. Immediate intervention may be needed."
        else:
            diary = f"{plant.common_name} health status is {health_status}. Continue monitoring."
        
        # Combine with user observations
        if observations:
            diary += f" User noted: {observations}."
        
        # Generate recommended action
        if recommendations:
            action = recommendations[0]
        elif health_status == "healthy":
            action = "Continue current care routine. Upload a photo tomorrow for trend tracking."
        elif health_status == "diseased":
            action = "Disease detected. Apply recommended treatment and increase monitoring frequency."
        else:
            action = "Monitor plant closely. Consider uploading another photo for better assessment."
        
        return AnalysisResult(
            health_score=health_score,
            visible_issues=visible_issues if visible_issues else ["none"],
            soil_moisture="moderate",  # Plant.id doesn't detect moisture
            recommended_action=action,
            flag_urgent=is_urgent,
            diary_entry=diary,
        )

    def _rule_based_analysis(self, plant: Plant, observations: str) -> AnalysisResult:
        """Fallback rule-based analysis when no AI is available."""
        obs_lower = observations.lower() if observations else ""
        
        if "yellow" in obs_lower or "droop" in obs_lower:
            return AnalysisResult(
                health_score=5,
                visible_issues=["yellowing", "wilting"],
                soil_moisture="check soil",
                recommended_action="Inspect soil moisture. May need water or better drainage.",
                flag_urgent=True,
                diary_entry=f"{plant.common_name} shows stress symptoms. Yellowing and wilting observed.",
            )
        
        if "brown" in obs_lower or "crisp" in obs_lower:
            return AnalysisResult(
                health_score=4,
                visible_issues=["leaf burn", "dry edges"],
                soil_moisture="likely dry",
                recommended_action="Check soil moisture. May be underwatered or receiving too much direct sun.",
                flag_urgent=True,
                diary_entry=f"{plant.common_name} shows signs of drought stress or leaf burn.",
            )
        
        if "spots" in obs_lower or "mold" in obs_lower:
            return AnalysisResult(
                health_score=4,
                visible_issues=["spots", "fungal growth"],
                soil_moisture="may be too wet",
                recommended_action="Check for fungal infection. Reduce watering and improve air circulation.",
                flag_urgent=True,
                diary_entry=f"{plant.common_name} shows potential fungal issues. Spots or mold visible.",
            )
        
        return AnalysisResult(
            health_score=8,
            visible_issues=["healthy foliage"],
            soil_moisture="adequate",
            recommended_action="Continue current routine. Upload a photo tomorrow for trend tracking.",
            flag_urgent=False,
            diary_entry=f"{plant.common_name} looks stable and healthy today.",
        )


def get_analysis_service(settings: Settings) -> AnalysisService:
    """Factory function to create AnalysisService with dependencies."""
    from app.services.gemini import GeminiService
    from app.services.plantid import PlantIdService
    
    gemini = GeminiService(settings)
    plantid = PlantIdService(settings)
    
    return AnalysisService(gemini, plantid)