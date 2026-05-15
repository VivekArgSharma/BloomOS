from __future__ import annotations

from app.core.config import Settings
from app.models.schemas import CareProfile, PlantCatalogItem, PlantIdentificationResponse
from app.services.gemini import GeminiService
from app.services.plantnet import PlantNetService


CARE_PROFILE_SCHEMA = """
{
  "water_interval_days": number,
  "light": string,
  "humidity": string,
  "fertilizer": string,
  "soil": string,
  "notes": string[]
}
""".strip()


class CatalogService:
    def __init__(self, store, gemini: GeminiService, plantnet: PlantNetService) -> None:
        self.store = store
        self.gemini = gemini
        self.plantnet = plantnet

    def identify(
        self, 
        query_hint: str, 
        image_bytes: bytes | None = None, 
        mime_type: str | None = None,
        filename: str | None = None,
    ) -> PlantIdentificationResponse:
        # First try catalog search by hint
        match = self.store.search_catalog(query_hint) if query_hint else None
        if match is not None:
            return PlantIdentificationResponse(
                matched_catalog=True,
                confidence=0.96,
                plant=match,
                rationale="Matched directly against the preloaded catalog.",
            )

        # If no image, use fallback
        if not image_bytes:
            fallback = self.store.find_catalog_by_name("Pothos") or self.store.list_catalog()[0]
            return PlantIdentificationResponse(
                matched_catalog=False,
                confidence=0.4,
                plant=fallback,
                rationale="No image provided. Using a starter plant profile.",
            )

        # Use PlantNet for identification
        if self.plantnet.enabled:
            plantnet_result = self.plantnet.identify(
                image_bytes,
                filename=(filename or "plant.jpg"),
                mime_type=(mime_type or "image/jpeg"),
            )
            if plantnet_result:
                # Try to find a match in our catalog
                common_name = plantnet_result.get("common_name", "")
                scientific_name = plantnet_result.get("scientific_name", "")
                
                ai_match = (
                    self.store.find_catalog_by_name(common_name) or
                    self.store.find_catalog_by_name(scientific_name)
                )
                
                if ai_match:
                    return PlantIdentificationResponse(
                        matched_catalog=True,
                        confidence=plantnet_result.get("score", 0) / 100,
                        plant=ai_match,
                        rationale=f"PlantNet identified as {common_name} and matched with catalog plant.",
                    )
                
                # No catalog match - use OpenRouter to generate care profile
                if self.gemini.enabled:
                    care_profile = self._generate_care_profile_with_ai(
                        common_name, 
                        scientific_name,
                        plantnet_result.get("genus", "")
                    )
                    if care_profile:
                        plant = PlantCatalogItem(
                            common_name=common_name,
                            species_name=scientific_name,
                            difficulty="moderate",
                            tags=["identified", plantnet_result.get("genus", "")],
                            care_profile=care_profile,
                        )
                        return PlantIdentificationResponse(
                            matched_catalog=False,
                            confidence=plantnet_result.get("score", 0) / 100,
                            plant=plant,
                            rationale=f"PlantNet identified {common_name}. Generated care profile with AI.",
                        )
                
                # Fallback if AI not available
                fallback = self.store.find_catalog_by_name("Pothos") or self.store.list_catalog()[0]
                return PlantIdentificationResponse(
                    matched_catalog=False,
                    confidence=plantnet_result.get("score", 0) / 100,
                    plant=fallback,
                    rationale=f"PlantNet identified {common_name}. Using fallback profile.",
                )

        # PlantNet not available - try Gemini/OpenRouter
        if self.gemini.enabled:
            return self._identify_with_gemini(query_hint, image_bytes, mime_type)
        
        # Fallback
        fallback = self.store.find_catalog_by_name("Pothos") or self.store.list_catalog()[0]
        return PlantIdentificationResponse(
            matched_catalog=False,
            confidence=0.4,
            plant=fallback,
            rationale="No identification service available. Using fallback plant.",
        )

    def _generate_care_profile_with_ai(
        self, 
        common_name: str, 
        scientific_name: str,
        genus: str
    ) -> CareProfile | None:
        """Generate care profile using OpenRouter (LLM)."""
        prompt = f"""Generate a care profile for a plant:
- Common name: {common_name}
- Scientific name: {scientific_name}
- Genus: {genus}

Respond with valid JSON only, no markdown:
{{
  "water_interval_days": number,
  "light": string,
  "humidity": string,
  "fertilizer": string,
  "soil": string,
  "notes": string[]
}}"""

        try:
            result = self.gemini.generate_json(
                prompt=prompt,
                schema_hint=CARE_PROFILE_SCHEMA,
            )
            return CareProfile(**result)
        except Exception as e:
            print(f"Error generating care profile: {e}")
            return None

    def _identify_with_gemini(
        self, 
        query_hint: str, 
        image_bytes: bytes, 
        mime_type: str | None
    ) -> PlantIdentificationResponse:
        """Fallback identification using Gemini/OpenRouter."""
        prompt = (
            f"Identify the plant from the image and generate a practical care profile. "
            f"User hint: {query_hint or 'none'}"
        )
        
        schema = """
        {
          "common_name": string,
          "species_name": string,
          "difficulty": "easy" | "moderate" | "advanced",
          "tags": string[],
          "confidence": number,
          "care_profile": {
            "water_interval_days": number,
            "light": string,
            "humidity": string,
            "fertilizer": string,
            "soil": string,
            "notes": string[]
          }
        }
        """.strip()

        payload = self.gemini.generate_json(
            prompt=prompt,
            schema_hint=schema,
            image_bytes=image_bytes,
            mime_type=mime_type,
        )
        
        ai_match = (
            self.store.find_catalog_by_name(payload.get("common_name", "")) or
            self.store.find_catalog_by_name(payload.get("species_name", ""))
        )
        
        plant = ai_match or PlantCatalogItem(
            common_name=payload["common_name"],
            species_name=payload["species_name"],
            difficulty=payload.get("difficulty", "moderate"),
            tags=payload.get("tags", []),
            care_profile=CareProfile(**payload["care_profile"]),
        )
        
        return PlantIdentificationResponse(
            matched_catalog=ai_match is not None,
            confidence=float(payload.get("confidence", 0.75)),
            plant=plant,
            rationale="Gemini identified the plant and generated a care profile.",
        )

    def list_catalog(self) -> list[PlantCatalogItem]:
        return self.store.list_catalog()
