from __future__ import annotations

import httpx

from app.core.config import Settings
from app.models.schemas import WeatherResponse


class WeatherService:
    def __init__(self, settings: Settings) -> None:
        self.settings = settings

    async def get_weather(self, city: str | None) -> WeatherResponse:
        resolved_city = city or "Bengaluru"
        if not self.settings.openweathermap_api_key:
            return WeatherResponse(
                city=resolved_city,
                summary="Warm, partly cloudy",
                temperature_c=27,
                humidity=61,
                rain_chance=18,
            )

        async with httpx.AsyncClient(timeout=15) as client:
            response = await client.get(
                "https://api.openweathermap.org/data/2.5/weather",
                params={"q": resolved_city, "appid": self.settings.openweathermap_api_key, "units": "metric"},
            )
            response.raise_for_status()
            payload = response.json()

        weather = payload.get("weather") or [{}]
        main = payload.get("main") or {}
        clouds = payload.get("clouds") or {}
        rain_chance = int(clouds.get("all", 0))
        return WeatherResponse(
            city=payload.get("name", resolved_city),
            summary=weather[0].get("description", "weather unavailable").title(),
            temperature_c=round(main.get("temp", 27)),
            humidity=round(main.get("humidity", 60)),
            rain_chance=rain_chance,
        )
