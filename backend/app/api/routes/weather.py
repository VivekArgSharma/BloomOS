from fastapi import APIRouter, Depends

from app.core.auth import CurrentUser, get_current_user
from app.core.config import Settings, get_settings
from app.models.schemas import WeatherResponse
from app.services.weather import WeatherService


router = APIRouter(prefix="/weather")


@router.get("", response_model=WeatherResponse)
async def get_weather(
    city: str | None = None,
    user: CurrentUser = Depends(get_current_user),
    settings: Settings = Depends(get_settings),
) -> WeatherResponse:
    return await WeatherService(settings).get_weather(city)
