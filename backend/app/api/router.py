from fastapi import APIRouter

from app.api.routes import chat, gardens, plants, weather


api_router = APIRouter()
api_router.include_router(gardens.router, tags=["gardens"])
api_router.include_router(plants.router, tags=["plants"])
api_router.include_router(chat.router, tags=["chat"])
api_router.include_router(weather.router, tags=["weather"])
