from app.models.schemas import WeatherResponse


class WeatherService:
    def get_weather(self, city: str | None) -> WeatherResponse:
        resolved_city = city or "Bengaluru"
        return WeatherResponse(
            city=resolved_city,
            summary="Warm, partly cloudy",
            temperature_c=27,
            humidity=61,
            rain_chance=18,
        )
