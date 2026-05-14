from fastapi import APIRouter

from app.models.schemas import WeatherResponse
from app.services.weather import WeatherService


router = APIRouter(prefix="/weather")


@router.get("", response_model=WeatherResponse)
def get_weather(city: str | None = None) -> WeatherResponse:
    return WeatherService().get_weather(city)
