from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta
from uuid import UUID


@dataclass
class Badge:
    id: str
    name: str
    description: str
    icon: str
    unlocked: bool = False


class GamificationService:
    BADGES = [
        Badge(
            id="first-plant",
            name="Green Thumb Beginnings",
            description="Added your first plant to a garden",
            icon="🌱",
        ),
        Badge(
            id="seven-day-streak",
            name="Consistency Champion",
            description="Completed tasks for 7 consecutive days",
            icon="🔥",
        ),
        Badge(
            id="photo-streak",
            name="Daily Photographer",
            description="Uploaded photos for 5 days in a row",
            icon="📸",
        ),
        Badge(
            id="healthy-plant",
            name="Thriving Garden",
            description="Kept a plant at 90%+ health for a week",
            icon="🌿",
        ),
        Badge(
            id="recovery-success",
            name="Plant Rescuer",
            description="Successfully brought a plant out of recovery mode",
            icon="💚",
        ),
        Badge(
            id="multi-garden",
            name="Garden Curator",
            description="Created 3 or more gardens",
            icon="🏡",
        ),
        Badge(
            id="ten-plants",
            name="Plant Parent",
            description="Added 10 plants to your collection",
            icon="🌺",
        ),
        Badge(
            id="perfect-week",
            name="Perfect Week",
            description="100% task completion for an entire week",
            icon="⭐",
        ),
        Badge(
            id="chat-explorer",
            name="Curious Gardener",
            description="Asked 10 questions to the plant chatbot",
            icon="💬",
        ),
        Badge(
            id="weather-aware",
            name="Weather Wise",
            description="Skipped watering correctly due to rain forecast",
            icon="🌧️",
        ),
    ]

    def calculate_badges(
        self,
        garden_count: int,
        plant_count: int,
        task_completion_streak: int,
        photo_streak: int,
        recovery_achievements: int,
        perfect_weeks: int,
        chat_questions: int,
        weather_skips: int,
        plants_at_90_health: int,
    ) -> list[Badge]:
        unlocked = []
        
        if plant_count >= 1:
            badge = self._find_badge("first-plant")
            badge.unlocked = True
            unlocked.append(badge)
        
        if task_completion_streak >= 7:
            badge = self._find_badge("seven-day-streak")
            badge.unlocked = True
            unlocked.append(badge)
        
        if photo_streak >= 5:
            badge = self._find_badge("photo-streak")
            badge.unlocked = True
            unlocked.append(badge)
        
        if plants_at_90_health >= 1:
            badge = self._find_badge("healthy-plant")
            badge.unlocked = True
            unlocked.append(badge)
        
        if recovery_achievements >= 1:
            badge = self._find_badge("recovery-success")
            badge.unlocked = True
            unlocked.append(badge)
        
        if garden_count >= 3:
            badge = self._find_badge("multi-garden")
            badge.unlocked = True
            unlocked.append(badge)
        
        if plant_count >= 10:
            badge = self._find_badge("ten-plants")
            badge.unlocked = True
            unlocked.append(badge)
        
        if perfect_weeks >= 1:
            badge = self._find_badge("perfect-week")
            badge.unlocked = True
            unlocked.append(badge)
        
        if chat_questions >= 10:
            badge = self._find_badge("chat-explorer")
            badge.unlocked = True
            unlocked.append(badge)
        
        if weather_skips >= 1:
            badge = self._find_badge("weather-aware")
            badge.unlocked = True
            unlocked.append(badge)
        
        return unlocked

    def _find_badge(self, badge_id: str) -> Badge:
        for badge in self.BADGES:
            if badge.id == badge_id:
                return Badge(
                    id=badge.id,
                    name=badge.name,
                    description=badge.description,
                    icon=badge.icon,
                    unlocked=False,
                )
        return Badge(id=badge_id, name=badge_id, description="", icon="🏆")


@dataclass
class UserStats:
    garden_count: int
    plant_count: int
    current_streak: int
    longest_streak: int
    total_tasks_completed: int
    total_photos_uploaded: int
    recovery_mode_exits: int
    chat_questions_asked: int
    weather_decisions: int
    plants_at_health_90_plus: int


def calculate_user_stats(
    garden_count: int,
    plant_count: int,
    current_streak: int = 0,
    longest_streak: int = 0,
    total_tasks_completed: int = 0,
    total_photos_uploaded: int = 0,
    recovery_mode_exits: int = 0,
    chat_questions_asked: int = 0,
    weather_decisions: int = 0,
    plants_at_health_90_plus: int = 0,
) -> UserStats:
    return UserStats(
        garden_count=garden_count,
        plant_count=plant_count,
        current_streak=current_streak,
        longest_streak=longest_streak,
        total_tasks_completed=total_tasks_completed,
        total_photos_uploaded=total_photos_uploaded,
        recovery_mode_exits=recovery_mode_exits,
        chat_questions_asked=chat_questions_asked,
        weather_decisions=weather_decisions,
        plants_at_health_90_plus=plants_at_health_90_plus,
    )