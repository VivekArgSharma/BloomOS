from app.db.mock_store import MockStore
from app.models.schemas import PlantCatalogItem, PlantIdentificationResponse


class CatalogService:
    def __init__(self, store: MockStore) -> None:
        self.store = store

    def identify(self, query_hint: str) -> PlantIdentificationResponse:
        match = self.store.search_catalog(query_hint) if query_hint else None
        if match is None:
            match = self.store.find_catalog_by_name("Pothos")
            assert match is not None
            return PlantIdentificationResponse(
                matched_catalog=False,
                confidence=0.42,
                plant=match,
                rationale="No close catalog match was found from the upload hint, so a safe starter profile is suggested until Gemini or manual review confirms the species.",
            )
        return PlantIdentificationResponse(
            matched_catalog=True,
            confidence=0.93,
            plant=match,
            rationale="Matched against the preloaded plant catalog, so no Gemini call is required for this onboarding flow.",
        )

    def list_catalog(self) -> list[PlantCatalogItem]:
        return self.store.list_catalog()
