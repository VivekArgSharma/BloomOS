from fastapi import APIRouter

from app.api.routes import chat, gardens, plants, preview, weather, user


api_router = APIRouter()
api_router.include_router(gardens.router, tags=["gardens"])
api_router.include_router(plants.router, tags=["plants"])
api_router.include_router(preview.router, tags=["preview"])
api_router.include_router(chat.router, tags=["chat"])
api_router.include_router(weather.router, tags=["weather"])
api_router.include_router(user.router, tags=["user"])
