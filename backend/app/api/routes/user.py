from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException

from app.core.auth import CurrentUser, get_current_user
from app.core.deps import get_store
from app.models.schemas import Badge as BadgeSchema, CompatibilityCheck, UserBadges, UserStats
from app.services.compatibility import check_plant_compatibility
from app.services.gamification import GamificationService


router = APIRouter()


@router.get("/plants/{plant_id}/compatibility", response_model=CompatibilityCheck)
def get_plant_compatibility(
    plant_id: UUID,
    location_type: str,
    store=Depends(get_store),
    user: CurrentUser = Depends(get_current_user),
) -> CompatibilityCheck:
    plant = store.get_plant(user.id, plant_id)
    if plant is None:
        raise HTTPException(status_code=404, detail="Plant not found")
    
    garden = store.get_garden(user.id, plant.garden_id)
    city = garden.city if garden else None
    
    result = check_plant_compatibility(plant, location_type, city)
    return CompatibilityCheck(**result)


@router.get("/badges", response_model=UserBadges)
def get_user_badges(store=Depends(get_store), user: CurrentUser = Depends(get_current_user)) -> UserBadges:
    gardens = store.list_gardens(user.id)
    garden_count = len(gardens)
    
    plants = []
    for garden in gardens:
        garden_plants = store.list_garden_plants(user.id, garden.id)
        plants.extend(garden_plants)
    
    plant_count = len(plants)
    
    current_streak = 0
    longest_streak = 0
    total_tasks = 0
    total_photos = 0
    recovery_exits = 0
    plants_at_90_plus = 0
    perfect_weeks = 0
    
    for plant in plants:
        analytics = store.get_plant_analytics(user.id, plant.id)
        if analytics:
            current_streak = max(current_streak, analytics.streak_days)
            longest_streak = max(longest_streak, analytics.streak_days)
            total_tasks += analytics.task_completion_rate
        
        logs = store.list_logs(user.id, plant.id)
        total_photos += len(logs)
        
        if plant.current_health_score >= 9:
            plants_at_90_plus += 1
        
        if plant.recovery_mode:
            recovery_exits += 1
    
    gamification = GamificationService()
    badge_data = gamification.calculate_badges(
        garden_count=garden_count,
        plant_count=plant_count,
        task_completion_streak=current_streak,
        photo_streak=min(total_photos // 5, 10),
        recovery_achievements=recovery_exits,
        perfect_weeks=perfect_weeks,
        chat_questions=0,
        weather_skips=0,
        plants_at_90_health=plants_at_90_plus,
    )
    
    badges = [
        BadgeSchema(
            id=b.id,
            name=b.name,
            description=b.description,
            icon=b.icon,
            unlocked=b.unlocked,
        )
        for b in badge_data
    ]
    
    return UserBadges(
        badges=badges,
        total_unlocked=len(badges),
        total_available=len(GamificationService.BADGES),
    )


@router.get("/stats", response_model=UserStats)
def get_user_stats(store=Depends(get_store), user: CurrentUser = Depends(get_current_user)) -> UserStats:
    gardens = store.list_gardens(user.id)
    garden_count = len(gardens)
    
    plants = []
    for garden in gardens:
        garden_plants = store.list_garden_plants(user.id, garden.id)
        plants.extend(garden_plants)
    
    plant_count = len(plants)
    total_photos = 0
    plants_at_90_plus = 0
    
    for plant in plants:
        logs = store.list_logs(user.id, plant.id)
        total_photos += len(logs)
        if plant.current_health_score >= 9:
            plants_at_90_plus += 1
    
    return UserStats(
        garden_count=garden_count,
        plant_count=plant_count,
        current_streak=0,
        longest_streak=0,
        total_tasks_completed=0,
        total_photos_uploaded=total_photos,
        recovery_mode_exits=0,
        chat_questions_asked=0,
        weather_decisions=0,
        plants_at_health_90_plus=plants_at_90_plus,
    )