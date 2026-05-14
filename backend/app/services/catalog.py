from __future__ import annotations

from app.models.schemas import CareProfile, PlantCatalogItem, PlantIdentificationResponse
from app.services.gemini import GeminiService


IDENTIFY_SCHEMA = """
{
  \"common_name\": string,
  \"species_name\": string,
  \"difficulty\": \"easy\" | \"moderate\" | \"advanced\",
  \"tags\": string[],
  \"confidence\": number,
  \"rationale\": string,
  \"care_profile\": {
    \"water_interval_days\": number,
    \"light\": string,
    \"humidity\": string,
    \"fertilizer\": string,
    \"soil\": string,
    \"notes\": string[]
  }
}
""".strip()


class CatalogService:
    def __init__(self, store, gemini: GeminiService) -> None:
        self.store = store
        self.gemini = gemini

    def identify(self, query_hint: str, image_bytes: bytes | None = None, mime_type: str | None = None) -> PlantIdentificationResponse:
        match = self.store.search_catalog(query_hint) if query_hint else None
        if match is not None:
            return PlantIdentificationResponse(
                matched_catalog=True,
                confidence=0.96,
                plant=match,
                rationale="Matched directly against the preloaded catalog, so onboarding can skip Gemini.",
            )

        if not image_bytes or not self.gemini.enabled:
            fallback = self.store.find_catalog_by_name("Pothos") or self.store.list_catalog()[0]
            return PlantIdentificationResponse(
                matched_catalog=False,
                confidence=0.4,
                plant=fallback,
                rationale="No strong catalog match was found and Gemini is unavailable, so a safe starter profile is suggested.",
            )

        payload = self.gemini.generate_json(
            prompt=(
                "Identify the plant from the image and generate a practical care profile for a consumer gardening app. "
                f"The user hint is: {query_hint or 'none'}"
            ),
            schema_hint=IDENTIFY_SCHEMA,
            image_bytes=image_bytes,
            mime_type=mime_type,
        )
        ai_match = self.store.find_catalog_by_name(payload.get("common_name", "")) or self.store.find_catalog_by_name(
            payload.get("species_name", "")
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
            rationale=payload.get("rationale", "Gemini identified the plant and generated a care profile."),
        )

    def list_catalog(self) -> list[PlantCatalogItem]:
        return self.store.list_catalog()
