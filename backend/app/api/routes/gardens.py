from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException

from app.core.auth import CurrentUser, get_current_user
from app.core.deps import get_store
from app.models.schemas import Garden, GardenAnalytics, GardenCreate, Plant


router = APIRouter(prefix="/gardens")


@router.get("", response_model=list[Garden])
def list_gardens(store=Depends(get_store), user: CurrentUser = Depends(get_current_user)) -> list[Garden]:
    return store.list_gardens(user.id)


@router.post("", response_model=Garden, status_code=201)
def create_garden(payload: GardenCreate, store=Depends(get_store), user: CurrentUser = Depends(get_current_user)) -> Garden:
    return store.create_garden(user.id, payload)


@router.get("/{garden_id}/plants", response_model=list[Plant])
def list_garden_plants(garden_id: UUID, store=Depends(get_store), user: CurrentUser = Depends(get_current_user)) -> list[Plant]:
    garden = store.get_garden(user.id, garden_id)
    if garden is None:
        raise HTTPException(status_code=404, detail="Garden not found")
    return store.list_garden_plants(user.id, garden_id)


@router.get("/{garden_id}/analytics", response_model=GardenAnalytics)
def get_garden_analytics(garden_id: UUID, store=Depends(get_store), user: CurrentUser = Depends(get_current_user)) -> GardenAnalytics:
    analytics = store.get_garden_analytics(user.id, garden_id)
    if analytics is None:
        raise HTTPException(status_code=404, detail="Garden not found")
    return analytics
