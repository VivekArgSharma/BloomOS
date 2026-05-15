from __future__ import annotations

import base64
from typing import Any

import httpx

from app.core.config import Settings


class PlantIdService:
    BASE_URL = "https://api.plant.id/v2"
    
    def __init__(self, settings: Settings) -> None:
        self.api_key = settings.plantid_api_key
        self.timeout = 30
    
    @property
    def enabled(self) -> bool:
        return bool(self.api_key)
    
    def analyze_health(
        self, 
        image_bytes: bytes, 
        plant_type: str = "auto",
        health: str = "all"
    ) -> dict[str, Any] | None:
        """
        Analyze plant health and detect diseases using Plant.id API.
        
        Args:
            image_bytes: The image data
            plant_type: Type of plant (auto, crop, weed, etc.)
            health: Health assessment type (all, dead, healthy, diseased)
        
        Returns:
            Health analysis results with disease detection, health score, etc.
        """
        if not self.enabled:
            return None
        
        url = f"{self.BASE_URL}/identify"
        
        # Convert image to base64
        image_b64 = base64.b64encode(image_bytes).decode('utf-8')
        
        headers = {
            "Content-Type": "application/json",
            "Api-Key": self.api_key,
        }
        
        payload = {
            "images": [f"data:image/jpeg;base64,{image_b64}"],
            "latitude": 0,
            "longitude": 0,
            "similar_images": False,
            "health": "all",
            "disease_details": [
                "description",
                "common_names",
                "classification",
                "treatment",
                "cause",
            ],
        }
        
        try:
            resp = httpx.post(url, json=payload, headers=headers, timeout=self.timeout)
            resp.raise_for_status()
            data = resp.json()
            return self._parse_health_results(data)
        except httpx.HTTPStatusError as e:
            print(f"Plant.id HTTP error: {e.response.status_code} - {e.response.text}")
            return None
        except Exception as e:
            print(f"Plant.id error: {e}")
            return None
    
    def _parse_health_results(self, data: dict) -> dict[str, Any]:
        """
        Parse Plant.id API response to extract health and disease information.
        """
        suggestions = data.get("suggestions", [])
        
        if not suggestions:
            return self._empty_health_result()
        
        # Get the first (best) suggestion
        suggestion = suggestions[0]
        
        # Extract health assessment
        health_assessment = suggestion.get("health_assessment", {})
        health_status = health_assessment.get("health_status", "unknown")
        probability = health_assessment.get("probability", 0)
        
        # Extract disease information
        diseases = []
        plant_details = suggestion.get("plant_details", {})
        
        # Check for diseases in the suggestion
        if "disease" in suggestion:
            disease_info = suggestion.get("disease", {})
            diseases.append({
                "name": disease_info.get("name", "Unknown disease"),
                "probability": disease_info.get("probability", 0),
                "description": disease_info.get("description", ""),
            })
        
        # Extract treatment/recommendations
        treatment = suggestion.get("treatment", {})
        recommendations = treatment.get("prevention", []) + treatment.get("chemical", []) if treatment else []
        
        # Calculate health score (1-10)
        health_score = self._calculate_health_score(health_status, probability)
        
        # Extract visible issues
        visible_issues = []
        if health_status == "diseased":
            visible_issues.append("disease_detected")
        if health_status == "dead":
            visible_issues.append("plant_dead")
        
        # Determine if urgent
        is_urgent = health_status in ["diseased", "dead"] and probability > 0.7
        
        return {
            "health_score": health_score,
            "health_status": health_status,
            "confidence": round(probability * 100, 1),
            "diseases": diseases[:3],  # Limit to 3
            "visible_issues": visible_issues,
            "recommendations": recommendations[:5],  # Limit to 5
            "is_urgent": is_urgent,
            "plant_type": suggestion.get("plant_name", "Unknown"),
        }
    
    def _calculate_health_score(self, health_status: str, probability: float) -> int:
        """Convert health status to a 1-10 score."""
        status_scores = {
            "healthy": 9,
            "diseased": 4,
            "dead": 1,
            "unknown": 7,
        }
        
        base_score = status_scores.get(health_status, 7)
        # Adjust based on confidence
        confidence_factor = probability * 0.2  # Up to +/- 2 points
        
        score = round(base_score + (confidence_factor - 0.1) * 5)
        return max(1, min(10, score))  # Clamp between 1-10
    
    def _empty_health_result(self) -> dict[str, Any]:
        """Return default values when no results are available."""
        return {
            "health_score": 7,
            "health_status": "unknown",
            "confidence": 0,
            "diseases": [],
            "visible_issues": ["no_analysis"],
            "recommendations": [],
            "is_urgent": False,
            "plant_type": "Unknown",
        }


def get_plantid_service(settings: Settings) -> PlantIdService:
    return PlantIdService(settings)
