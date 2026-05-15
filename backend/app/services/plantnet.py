from __future__ import annotations

from typing import Any

import httpx

from app.core.config import Settings


class PlantNetService:
    BASE_URL = "https://my-api.plantnet.org/v2"
    
    def __init__(self, settings: Settings) -> None:
        self.api_key = settings.plantnet_api_key
        self.timeout = 30
    
    @property
    def enabled(self) -> bool:
        return bool(self.api_key)
    
    def identify(
        self,
        image_bytes: bytes,
        filename: str = "plant.jpg",
        mime_type: str = "image/jpeg",
    ) -> dict[str, Any] | None:
        """
        Identify plant species from an image using PlantNet API.
        Returns species information or None if not available.
        """
        if not self.enabled:
            return None
        
        url = f"{self.BASE_URL}/identify/all"
        params = {
            "api-key": self.api_key,
            "lang": "en",
            "include-related-images": "false",
            "no-reject": "true",
        }
        files = {
            "images": (filename, image_bytes, mime_type),
        }
        data = {
            "organs": "auto",
        }
        
        try:
            resp = httpx.post(url, params=params, data=data, files=files, timeout=self.timeout)
            resp.raise_for_status()
            data = resp.json()
            return self._parse_results(data)
        except httpx.HTTPStatusError as e:
            print(f"PlantNet HTTP error: {e.response.status_code} - {e.response.text}")
            return None
        except Exception as e:
            print(f"PlantNet error: {e}")
            return None
    
    def _parse_results(self, data: dict) -> dict[str, Any] | None:
        """
        Parse PlantNet API response to extract species information.
        """
        results = data.get("results", [])
        if not results:
            return None
        
        best_result = results[0]
        score = best_result.get("score", 0)
        
        # Extract scientific name and common names
        species = best_result.get("species", {})
        scientific_name = species.get("scientificNameWithoutAuthor", "")
        common_names = species.get("commonNames", [])[:3]  # Limit to 3
        
        genus = species.get("genus", {})
        genus_name = genus.get("scientificNameWithoutAuthor", "")
        
        return {
            "scientific_name": scientific_name,
            "common_name": common_names[0] if common_names else scientific_name,
            "common_names": common_names,
            "genus": genus_name,
            "score": round(score * 100, 1),
            "is_plant": True,
        }


def get_plantnet_service(settings: Settings) -> PlantNetService:
    return PlantNetService(settings)
