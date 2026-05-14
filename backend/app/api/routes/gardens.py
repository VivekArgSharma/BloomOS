from fastapi import APIRouter, Depends, HTTPException
from uuid import UUID

from app.core.deps import get_store
from app.db.mock_store import MockStore
from app.models.schemas import Garden, GardenCreate, Plant


router = APIRouter(prefix="/gardens")


@router.get("", response_model=list[Garden])
def list_gardens(store: MockStore = Depends(get_store)) -> list[Garden]:
    return store.list_gardens()


@router.post("", response_model=Garden, status_code=201)
def create_garden(payload: GardenCreate, store: MockStore = Depends(get_store)) -> Garden:
    return store.create_garden(payload)


@router.get("/{garden_id}/plants", response_model=list[Plant])
def list_garden_plants(garden_id: UUID, store: MockStore = Depends(get_store)) -> list[Plant]:
    plants = store.list_garden_plants(garden_id)
    if not plants and not any(garden.id == garden_id for garden in store.list_gardens()):
        raise HTTPException(status_code=404, detail="Garden not found")
    return plants
