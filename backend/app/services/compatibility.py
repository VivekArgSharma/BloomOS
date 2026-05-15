from __future__ import annotations

from uuid import UUID

from app.models.schemas import Plant, PlantCatalogItem


class CompatibilityService:
    LOCATION_CONDITIONS = {
        "balcony": {
            "light": ["full sun", "bright direct"],
            "humidity": ["low", "medium"],
            "temperature_range": (15, 35),
        },
        "indoor": {
            "light": ["bright indirect", "medium indirect", "low to bright indirect"],
            "humidity": ["medium", "medium-high", "high"],
            "temperature_range": (18, 28),
        },
        "terrace": {
            "light": ["full sun", "bright direct"],
            "humidity": ["low", "medium"],
            "temperature_range": (15, 38),
        },
        "garden": {
            "light": ["full sun", "bright direct", "bright indirect"],
            "humidity": ["low", "medium", "medium-high"],
            "temperature_range": (10, 35),
        },
    }

    def check_compatibility(
        self,
        plant: Plant | PlantCatalogItem,
        location_type: str,
        city: str | None = None,
    ) -> dict:
        location = self.LOCATION_CONDITIONS.get(location_type.lower(), self.LOCATION_CONDITIONS["indoor"])
        
        light_match = self._check_light_compatibility(plant.care_profile.light, location["light"])
        humidity_match = self._check_humidity_compatibility(plant.care_profile.humidity, location["humidity"])
        
        issues = []
        recommendations = []
        
        if not light_match["compatible"]:
            issues.append(light_match["issue"])
            recommendations.append(light_match["recommendation"])
        
        if not humidity_match["compatible"]:
            issues.append(humidity_match["issue"])
            recommendations.append(humidity_match["recommendation"])
        
        soil_issues = self._check_soil_requirements(plant.care_profile.soil)
        if soil_issues:
            issues.extend(soil_issues)
            recommendations.append("Ensure well-draining soil mix is used in containers.")
        
        overall_compatible = len([i for i in issues if "not recommended" in i.lower() or "may struggle" in i.lower()]) == 0
        confidence = max(0, 100 - len(issues) * 20)
        
        return {
            "compatible": overall_compatible,
            "confidence": confidence,
            "issues": issues,
            "recommendations": recommendations,
            "light_compatibility": light_match,
            "humidity_compatibility": humidity_match,
        }

    def _check_light_compatibility(self, plant_light: str, location_lights: list[str]) -> dict:
        plant_light_lower = plant_light.lower()
        
        for loc_light in location_lights:
            if any(keyword in plant_light_lower for keyword in loc_light.split()):
                return {
                    "compatible": True,
                    "match": f"Plant prefers {plant_light}, location provides {loc_light}",
                }
        
        if "low" in plant_light_lower or "shade" in plant_light_lower:
            return {
                "compatible": False,
                "issue": f"Plant needs {plant_light} but location is brighter",
                "recommendation": "Use sheer curtains to filter harsh direct sunlight",
            }
        
        if "full sun" in plant_light_lower or "bright direct" in plant_light_lower:
            return {
                "compatible": False,
                "issue": f"Plant needs {plant_light} which may not be available",
                "recommendation": "Place near a south-facing window or outdoor area with full sun",
            }
        
        return {
            "compatible": True,
            "match": f"Plant light needs may work in this location",
        }

    def _check_humidity_compatibility(self, plant_humidity: str, location_humidities: list[str]) -> dict:
        plant_hum_lower = plant_humidity.lower()
        
        humidity_map = {
            "low": 30,
            "medium": 50,
            "medium-high": 65,
            "high": 80,
        }
        
        plant_humidity_level = humidity_map.get(plant_hum_lower, 50)
        
        for loc_hum in location_humidities:
            loc_hum_level = humidity_map.get(loc_hum.lower(), 50)
            if abs(plant_humidity_level - loc_hum_level) <= 20:
                return {
                    "compatible": True,
                    "match": f"Plant prefers {plant_humidity}, location typically has {loc_hum}",
                }
        
        if plant_humidity_level > 60:
            return {
                "compatible": False,
                "issue": f"Plant needs high humidity ({plant_humidity}) but location may be drier",
                "recommendation": "Use a humidifier, mist regularly, or group with other plants",
            }
        
        if plant_humidity_level < 40:
            return {
                "compatible": False,
                "issue": f"Plant prefers {plant_humidity} but location may be more humid",
                "recommendation": "Ensure good ventilation to prevent fungal issues",
            }
        
        return {
            "compatible": True,
            "match": f"Plant humidity needs should work in this location",
        }

    def _check_soil_requirements(self, soil: str) -> list[str]:
        issues = []
        
        if "succulent" in soil.lower() or "cactus" in soil.lower():
            issues.append("This plant needs fast-draining soil - regular potting mix may cause root rot")
        
        if "moisture-retentive" in soil.lower():
            issues.append("Plant needs consistent moisture - monitor watering closely in containers")
        
        return issues


def check_plant_compatibility(
    plant: Plant | PlantCatalogItem,
    location_type: str,
    city: str | None = None,
) -> dict:
    return CompatibilityService().check_compatibility(plant, location_type, city)