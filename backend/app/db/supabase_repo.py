from __future__ import annotations

from collections import defaultdict
from datetime import date, datetime
import re
from typing import Any
from uuid import UUID

from supabase import Client

from app.core.config import Settings
from app.models.schemas import (
    AnalysisResult,
    CareProfile,
    CompletionPoint,
    CommunityComment,
    CommunityFeedResponse,
    CommunityLikeResponse,
    CommunityPost,
    CommunityPostCreate,
    CommunityPostUpdate,
    CommunityCommentCreate,
    CommunityCommentUpdate,
    CommunityProfile,
    CommunityProfilePage,
    CommunityProfileUpdate,
    DailyLog,
    DailyPlan,
    Garden,
    GardenAnalytics,
    GardenCreate,
    GardenPlantSnapshot,
    HealthPoint,
    IssueCount,
    Plant,
    PlantAnalytics,
    PlantCatalogItem,
    PlantCreate,
    TaskItem,
)


class SupabaseRepository:
    def __init__(self, client: Client, settings: Settings) -> None:
        self.client = client
        self.settings = settings

    def list_catalog(self) -> list[PlantCatalogItem]:
        data = self.client.table("plant_catalog").select("*").order("common_name").execute().data or []
        return [self._map_catalog_item(row) for row in data]

    def find_catalog_by_name(self, name: str) -> PlantCatalogItem | None:
        normalized = name.strip().lower()
        for item in self.list_catalog():
            if normalized in {item.common_name.lower(), item.species_name.lower()}:
                return item
        return None

    def search_catalog(self, query: str) -> PlantCatalogItem | None:
        normalized = query.strip().lower()
        if not normalized:
            return None
        for item in self.list_catalog():
            haystack = " ".join([item.common_name, item.species_name, *item.tags]).lower()
            if normalized in haystack:
                return item
        return None

    def list_gardens(self, user_id: str) -> list[Garden]:
        data = self.client.table("gardens").select("*").eq("user_id", user_id).order("created_at").execute().data or []
        gardens = [self._map_garden(row) for row in data]
        for garden in gardens:
            plants = self.list_garden_plants(user_id, garden.id)
            garden.plant_count = len(plants)
            garden.health_score = round(sum(plant.current_health_score for plant in plants) / len(plants) * 10) if plants else 0
        return gardens

    def get_garden(self, user_id: str, garden_id: UUID) -> Garden | None:
        row = self._get_garden_row(user_id, garden_id)
        if row is None:
            return None
        garden = self._map_garden(row)
        plants = self.list_garden_plants(user_id, garden_id)
        garden.plant_count = len(plants)
        garden.health_score = round(sum(plant.current_health_score for plant in plants) / len(plants) * 10) if plants else 0
        return garden

    def create_garden(self, user_id: str, payload: GardenCreate) -> Garden:
        data = (
            self.client.table("gardens")
            .insert(
                {
                    "user_id": user_id,
                    "name": payload.name,
                    "location_type": payload.location_type,
                    "city": payload.city,
                    "latitude": payload.latitude,
                    "longitude": payload.longitude,
                }
            )
            .execute()
            .data
        )
        return self._map_garden(data[0])

    def list_garden_plants(self, user_id: str, garden_id: UUID) -> list[Plant]:
        self._get_garden_row(user_id, garden_id)
        data = self.client.table("plants").select("*").eq("garden_id", str(garden_id)).order("added_at").execute().data or []
        return [self._map_plant(row) for row in data]

    def create_plant(self, user_id: str, payload: PlantCreate) -> Plant:
        self._get_garden_row(user_id, payload.garden_id)
        data = (
            self.client.table("plants")
            .insert(
                {
                    "garden_id": str(payload.garden_id),
                    "common_name": payload.common_name,
                    "species_name": payload.species_name,
                    "source": payload.source,
                    "care_profile": payload.care_profile.model_dump(),
                    "current_health_score": 8,
                    "recovery_mode": False,
                }
            )
            .execute()
            .data
        )
        return self._map_plant(data[0])

    def get_plant(self, user_id: str, plant_id: UUID) -> Plant | None:
        row = self._get_plant_row(user_id, plant_id)
        return self._map_plant(row) if row else None

    def list_logs(self, user_id: str, plant_id: UUID) -> list[DailyLog]:
        self._get_plant_row(user_id, plant_id)
        data = self.client.table("daily_logs").select("*").eq("plant_id", str(plant_id)).order("created_at", desc=True).execute().data or []
        return [self._map_log(row) for row in data]

    def save_analysis(self, user_id: str, plant_id: UUID, analysis: AnalysisResult, photo_url: str, observations: str) -> DailyLog:
        self._get_plant_row(user_id, plant_id)
        data = (
            self.client.table("daily_logs")
            .insert(
                {
                    "plant_id": str(plant_id),
                    "photo_url": photo_url,
                    "observations": observations,
                    "analysis_json": analysis.model_dump(),
                }
            )
            .execute()
            .data
        )
        self.client.table("plants").update(
            {"current_health_score": analysis.health_score, "recovery_mode": analysis.health_score < 5}
        ).eq("id", str(plant_id)).execute()
        return self._map_log(data[0])

    def get_plan(self, user_id: str, plant_id: UUID) -> DailyPlan | None:
        self._get_plant_row(user_id, plant_id)
        data = (
            self.client.table("daily_plans")
            .select("*")
            .eq("plant_id", str(plant_id))
            .eq("date", str(date.today()))
            .limit(1)
            .execute()
            .data
            or []
        )
        return self._map_plan(data[0]) if data else None

    def upsert_plan(self, user_id: str, plan: DailyPlan) -> DailyPlan:
        self._get_plant_row(user_id, plan.plant_id)
        data = (
            self.client.table("daily_plans")
            .upsert(
                {
                    "plant_id": str(plan.plant_id),
                    "date": str(plan.date),
                    "tasks": [task.model_dump() for task in plan.tasks],
                    "weather_snapshot": plan.weather_snapshot,
                    "generated_by_ai": plan.generated_by_ai,
                },
                on_conflict="plant_id,date",
            )
            .execute()
            .data
        )
        return self._map_plan(data[0])

    def get_recent_plans(self, user_id: str, plant_id: UUID, limit: int = 7) -> list[DailyPlan]:
        self._get_plant_row(user_id, plant_id)
        data = (
            self.client.table("daily_plans")
            .select("*")
            .eq("plant_id", str(plant_id))
            .order("date", desc=True)
            .limit(limit)
            .execute()
            .data
            or []
        )
        return [self._map_plan(row) for row in data]

    def complete_task(self, user_id: str, plant_id: UUID, task_id: str) -> TaskItem | None:
        plan = self.get_plan(user_id, plant_id)
        if plan is None:
            return None
        for task in plan.tasks:
            if task.id == task_id:
                task.completed = True
                updated = self.upsert_plan(user_id, plan)
                for saved_task in updated.tasks:
                    if saved_task.id == task_id:
                        return saved_task
        return None

    def progress_percent(self, user_id: str, plant_id: UUID) -> int:
        plan = self.get_plan(user_id, plant_id)
        if plan is None or not plan.tasks:
            return 0
        completed = sum(1 for task in plan.tasks if task.completed)
        return round((completed / len(plan.tasks)) * 100)

    def recent_grounding(self, user_id: str, plant_id: UUID) -> list[str]:
        plant = self.get_plant(user_id, plant_id)
        if plant is None:
            return []
        snippets = [
            f"{plant.common_name} generally prefers {plant.care_profile.light} light.",
            f"Water cadence is every {plant.care_profile.water_interval_days} days under normal conditions.",
        ]
        logs = self.list_logs(user_id, plant_id)
        if logs:
            latest = logs[0]
            snippets.append(
                f"Latest health score is {latest.analysis.health_score}/10 with issues: {', '.join(latest.analysis.visible_issues) or 'none'}."
            )
        return snippets

    def get_plant_analytics(self, user_id: str, plant_id: UUID) -> PlantAnalytics | None:
        plant = self.get_plant(user_id, plant_id)
        if plant is None:
            return None
        logs = list(reversed(self.list_logs(user_id, plant_id)))
        plans = list(reversed(self.get_recent_plans(user_id, plant_id, limit=7)))
        if not logs:
            return PlantAnalytics(
                plant_id=plant_id,
                current_health=plant.current_health_score,
                average_health=plant.current_health_score,
                health_delta=0,
                streak_days=0,
                task_completion_rate=0,
                watering_consistency=0,
                issue_breakdown=[],
                health_history=[],
                completion_history=[],
                insight="Upload daily photos to build this plant's analytics history.",
            )

        recent_logs = logs[-7:]
        scores = [log.analysis.health_score for log in recent_logs]
        issue_counts: dict[str, int] = defaultdict(int)
        for log in logs:
            for issue in log.analysis.visible_issues:
                issue_counts[issue] += 1

        completion_history = [
            CompletionPoint(
                label=plan.date.strftime("%a"),
                completed=sum(1 for task in plan.tasks if task.completed),
                total=len(plan.tasks),
                rate=round((sum(1 for task in plan.tasks if task.completed) / len(plan.tasks)) * 100) if plan.tasks else 0,
            )
            for plan in plans[-7:]
        ]
        avg_completion = round(sum(point.rate for point in completion_history) / len(completion_history)) if completion_history else 0
        streak = 0
        for point in reversed(completion_history):
            if point.rate >= 67:
                streak += 1
            else:
                break

        health_delta = scores[-1] - scores[0]
        watering_consistency = max(35, min(100, avg_completion - 5 + plant.care_profile.water_interval_days * 2))
        direction = "improving" if health_delta > 0 else "holding steady" if health_delta == 0 else "slipping"
        return PlantAnalytics(
            plant_id=plant_id,
            current_health=plant.current_health_score,
            average_health=round(sum(scores) / len(scores)),
            health_delta=health_delta,
            streak_days=streak,
            task_completion_rate=avg_completion,
            watering_consistency=watering_consistency,
            issue_breakdown=[IssueCount(issue=issue, count=count) for issue, count in sorted(issue_counts.items(), key=lambda item: item[1], reverse=True)],
            health_history=[HealthPoint(label=log.created_at.strftime("%a"), score=log.analysis.health_score) for log in recent_logs],
            completion_history=completion_history,
            insight=f"{plant.common_name} is {direction}; keep light and watering consistent for the next few days.",
        )

    def get_garden_analytics(self, user_id: str, garden_id: UUID) -> GardenAnalytics | None:
        garden = self._get_garden_row(user_id, garden_id)
        if garden is None:
            return None
        plants = self.list_garden_plants(user_id, garden_id)
        if not plants:
            return GardenAnalytics(
                garden_id=garden_id,
                overall_health=0,
                average_completion_rate=0,
                plants_in_recovery=0,
                issue_breakdown=[],
                health_history=[],
                plant_snapshots=[],
                recommended_focus="Add plants to start building garden analytics.",
            )

        plant_analytics = [self.get_plant_analytics(user_id, plant.id) for plant in plants]
        valid = [item for item in plant_analytics if item is not None]
        history_len = min((len(item.health_history) for item in valid), default=0)
        history: list[HealthPoint] = []
        for index in range(history_len):
            label = valid[0].health_history[index].label
            score = round(sum(item.health_history[index].score for item in valid) / len(valid))
            history.append(HealthPoint(label=label, score=score))

        issue_counts: dict[str, int] = defaultdict(int)
        for item in valid:
            for issue in item.issue_breakdown:
                issue_counts[issue.issue] += issue.count

        snapshots = [
            GardenPlantSnapshot(
                plant_id=plant.id,
                common_name=plant.common_name,
                health_score=plant.current_health_score,
                completion_rate=next((item.task_completion_rate for item in valid if item.plant_id == plant.id), 0),
                recovery_mode=plant.recovery_mode,
            )
            for plant in plants
        ]
        healthiest = max(plants, key=lambda plant: plant.current_health_score)
        needs_attention = min(plants, key=lambda plant: plant.current_health_score)
        avg_completion = round(sum(snapshot.completion_rate for snapshot in snapshots) / len(snapshots))
        return GardenAnalytics(
            garden_id=garden_id,
            overall_health=round(sum(plant.current_health_score for plant in plants) / len(plants) * 10),
            average_completion_rate=avg_completion,
            plants_in_recovery=sum(1 for plant in plants if plant.recovery_mode),
            healthiest_plant=healthiest.common_name,
            needs_attention_plant=needs_attention.common_name,
            issue_breakdown=[IssueCount(issue=issue, count=count) for issue, count in sorted(issue_counts.items(), key=lambda item: item[1], reverse=True)],
            health_history=history,
            plant_snapshots=snapshots,
            recommended_focus=f"Prioritize {needs_attention.common_name} and keep overall completion above {max(80, avg_completion)}%.",
        )

    def get_or_create_community_profile(self, user_id: str, user_email: str | None = None) -> CommunityProfile:
        existing = self.client.table("profiles").select("*").eq("id", user_id).limit(1).execute().data or []
        if existing:
            row = existing[0]
            updates: dict[str, Any] = {}
            if not row.get("username"):
                updates["username"] = self._build_username(user_id, user_email)
            if not row.get("name"):
                updates["name"] = self._build_display_name(user_email)
            if updates:
                updates["updated_at"] = datetime.utcnow().isoformat()
                row = self.client.table("profiles").update(updates).eq("id", user_id).execute().data[0]
            return self._map_community_profile(row)

        payload = {
            "id": user_id,
            "name": self._build_display_name(user_email),
            "username": self._build_username(user_id, user_email),
            "avatar_url": None,
            "bio": None,
            "is_public": True,
        }
        row = self.client.table("profiles").insert(payload).execute().data[0]
        return self._map_community_profile(row)

    def update_community_profile(self, user_id: str, user_email: str | None, payload: CommunityProfileUpdate) -> CommunityProfile:
        self.get_or_create_community_profile(user_id, user_email)
        updates = payload.model_dump(exclude_none=True)
        if "display_name" in updates:
            updates["name"] = updates.pop("display_name")
        if "username" in updates:
            updates["username"] = self._sanitize_username(updates["username"])
        if not updates:
            return self.get_or_create_community_profile(user_id, user_email)
        updates["updated_at"] = datetime.utcnow().isoformat()
        row = self.client.table("profiles").update(updates).eq("id", user_id).execute().data[0]
        return self._map_community_profile(row)

    def list_community_feed(self, user_id: str, user_email: str | None = None, limit: int = 20, offset: int = 0) -> CommunityFeedResponse:
        self.get_or_create_community_profile(user_id, user_email)
        rows = (
            self.client.table("community_posts")
            .select("*")
            .order("created_at", desc=True)
            .range(offset, offset + limit - 1)
            .execute()
            .data
            or []
        )
        next_offset = offset + limit if len(rows) == limit else None
        return CommunityFeedResponse(posts=[self._hydrate_community_post(user_id, row) for row in rows], next_offset=next_offset)

    def create_community_post(self, user_id: str, user_email: str | None, payload: CommunityPostCreate) -> CommunityPost:
        self.get_or_create_community_profile(user_id, user_email)
        row = (
            self.client.table("community_posts")
            .insert({"author_id": user_id, "body": payload.body.strip(), "image_url": payload.image_url})
            .execute()
            .data[0]
        )
        return self._hydrate_community_post(user_id, row)

    def update_community_post(self, user_id: str, post_id: UUID, payload: CommunityPostUpdate) -> CommunityPost:
        post = self._get_community_post_row(post_id)
        if post is None or post["author_id"] != user_id:
            raise ValueError("Post not found")
        row = (
            self.client.table("community_posts")
            .update({"body": payload.body.strip(), "image_url": payload.image_url, "updated_at": datetime.utcnow().isoformat()})
            .eq("id", str(post_id))
            .execute()
            .data[0]
        )
        return self._hydrate_community_post(user_id, row)

    def delete_community_post(self, user_id: str, post_id: UUID) -> None:
        post = self._get_community_post_row(post_id)
        if post is None or post["author_id"] != user_id:
            raise ValueError("Post not found")
        self.client.table("community_posts").delete().eq("id", str(post_id)).execute()

    def list_community_comments(self, user_id: str, user_email: str | None, post_id: UUID) -> list[CommunityComment]:
        self.get_or_create_community_profile(user_id, user_email)
        if self._get_community_post_row(post_id) is None:
            return []
        rows = (
            self.client.table("community_comments")
            .select("*")
            .eq("post_id", str(post_id))
            .order("created_at")
            .execute()
            .data
            or []
        )
        return [self._hydrate_community_comment(user_id, row) for row in rows]

    def create_community_comment(self, user_id: str, user_email: str | None, post_id: UUID, payload: CommunityCommentCreate) -> CommunityComment:
        self.get_or_create_community_profile(user_id, user_email)
        if self._get_community_post_row(post_id) is None:
            raise ValueError("Post not found")
        row = (
            self.client.table("community_comments")
            .insert({"post_id": str(post_id), "author_id": user_id, "body": payload.body.strip()})
            .execute()
            .data[0]
        )
        return self._hydrate_community_comment(user_id, row)

    def update_community_comment(self, user_id: str, comment_id: UUID, payload: CommunityCommentUpdate) -> CommunityComment:
        rows = self.client.table("community_comments").select("*").eq("id", str(comment_id)).limit(1).execute().data or []
        if not rows or rows[0]["author_id"] != user_id:
            raise ValueError("Comment not found")
        row = (
            self.client.table("community_comments")
            .update({"body": payload.body.strip(), "updated_at": datetime.utcnow().isoformat()})
            .eq("id", str(comment_id))
            .execute()
            .data[0]
        )
        return self._hydrate_community_comment(user_id, row)

    def delete_community_comment(self, user_id: str, comment_id: UUID) -> None:
        rows = self.client.table("community_comments").select("*").eq("id", str(comment_id)).limit(1).execute().data or []
        if not rows or rows[0]["author_id"] != user_id:
            raise ValueError("Comment not found")
        self.client.table("community_comments").delete().eq("id", str(comment_id)).execute()

    def toggle_community_like(self, user_id: str, user_email: str | None, post_id: UUID, liked: bool) -> CommunityLikeResponse:
        self.get_or_create_community_profile(user_id, user_email)
        if self._get_community_post_row(post_id) is None:
            raise ValueError("Post not found")
        if liked:
            self.client.table("community_post_likes").upsert({"post_id": str(post_id), "user_id": user_id}).execute()
        else:
            self.client.table("community_post_likes").delete().eq("post_id", str(post_id)).eq("user_id", user_id).execute()
        likes = self.client.table("community_post_likes").select("post_id", count="exact").eq("post_id", str(post_id)).execute()
        return CommunityLikeResponse(
            post_id=post_id,
            like_count=likes.count or 0,
            viewer_has_liked=liked,
        )

    def get_community_profile_page(self, viewer_user_id: str, username: str, limit: int = 20, offset: int = 0) -> CommunityProfilePage | None:
        profile_rows = self.client.table("profiles").select("*").ilike("username", username).limit(1).execute().data or []
        if not profile_rows:
            return None
        profile = self._map_community_profile(profile_rows[0])
        author_id = profile_rows[0]["id"]
        rows = (
            self.client.table("community_posts")
            .select("*")
            .eq("author_id", author_id)
            .order("created_at", desc=True)
            .range(offset, offset + limit - 1)
            .execute()
            .data
            or []
        )
        next_offset = offset + limit if len(rows) == limit else None
        return CommunityProfilePage(
            profile=profile,
            posts=[self._hydrate_community_post(viewer_user_id, row) for row in rows],
            next_offset=next_offset,
        )

    def _get_garden_row(self, user_id: str, garden_id: UUID) -> dict[str, Any] | None:
        data = (
            self.client.table("gardens").select("*").eq("id", str(garden_id)).eq("user_id", user_id).limit(1).execute().data or []
        )
        return data[0] if data else None

    def _get_plant_row(self, user_id: str, plant_id: UUID) -> dict[str, Any] | None:
        data = self.client.table("plants").select("*").eq("id", str(plant_id)).limit(1).execute().data or []
        if not data:
            return None
        plant = data[0]
        garden = self._get_garden_row(user_id, UUID(plant["garden_id"]))
        return plant if garden else None

    def _map_garden(self, row: dict[str, Any]) -> Garden:
        return Garden(
            id=UUID(row["id"]),
            user_id=row["user_id"],
            name=row["name"],
            location_type=row["location_type"],
            city=row.get("city"),
            latitude=row.get("latitude"),
            longitude=row.get("longitude"),
            created_at=datetime.fromisoformat(row["created_at"].replace("Z", "+00:00")),
        )

    def _map_plant(self, row: dict[str, Any]) -> Plant:
        return Plant(
            id=UUID(row["id"]),
            garden_id=UUID(row["garden_id"]),
            common_name=row["common_name"],
            species_name=row["species_name"],
            source=row.get("source", "catalog"),
            care_profile=CareProfile(**row["care_profile"]),
            current_health_score=row.get("current_health_score", 8),
            recovery_mode=row.get("recovery_mode", False),
            added_at=datetime.fromisoformat(row["added_at"].replace("Z", "+00:00")),
        )

    def _map_catalog_item(self, row: dict[str, Any]) -> PlantCatalogItem:
        return PlantCatalogItem(
            id=UUID(row["id"]),
            common_name=row["common_name"],
            species_name=row["species_name"],
            difficulty=row["difficulty"],
            tags=row.get("tags") or [],
            care_profile=CareProfile(**row["care_profile"]),
        )

    def _map_log(self, row: dict[str, Any]) -> DailyLog:
        return DailyLog(
            id=UUID(row["id"]),
            plant_id=UUID(row["plant_id"]),
            photo_url=row["photo_url"],
            observations=row.get("observations") or "",
            analysis=AnalysisResult(**row["analysis_json"]),
            created_at=datetime.fromisoformat(row["created_at"].replace("Z", "+00:00")),
        )

    def _map_plan(self, row: dict[str, Any]) -> DailyPlan:
        return DailyPlan(
            id=UUID(row["id"]),
            plant_id=UUID(row["plant_id"]),
            date=date.fromisoformat(row["date"]),
            tasks=[TaskItem(**task) for task in row.get("tasks") or []],
            weather_snapshot=row.get("weather_snapshot") or {},
            generated_by_ai=row.get("generated_by_ai", True),
        )

    def _get_community_post_row(self, post_id: UUID) -> dict[str, Any] | None:
        rows = self.client.table("community_posts").select("*").eq("id", str(post_id)).limit(1).execute().data or []
        return rows[0] if rows else None

    def _hydrate_community_post(self, viewer_user_id: str, row: dict[str, Any]) -> CommunityPost:
        profile_rows = self.client.table("profiles").select("*").eq("id", row["author_id"]).limit(1).execute().data or []
        like_result = self.client.table("community_post_likes").select("post_id", count="exact").eq("post_id", row["id"]).execute()
        liked_rows = self.client.table("community_post_likes").select("post_id").eq("post_id", row["id"]).eq("user_id", viewer_user_id).limit(1).execute().data or []
        comment_result = self.client.table("community_comments").select("post_id", count="exact").eq("post_id", row["id"]).execute()
        profile = self._map_community_profile(profile_rows[0] if profile_rows else {"id": row["author_id"], "name": "Plant Lover", "username": f"grower-{row['author_id'][:8]}"})
        return CommunityPost(
            id=UUID(row["id"]),
            author=profile,
            body=row["body"],
            image_url=row.get("image_url"),
            like_count=like_result.count or 0,
            comment_count=comment_result.count or 0,
            viewer_has_liked=bool(liked_rows),
            created_at=datetime.fromisoformat(row["created_at"].replace("Z", "+00:00")),
            is_owner=row["author_id"] == viewer_user_id,
            updated_at=datetime.fromisoformat(row["updated_at"].replace("Z", "+00:00")) if row.get("updated_at") else None,
        )

    def _hydrate_community_comment(self, viewer_user_id: str, row: dict[str, Any]) -> CommunityComment:
        profile_rows = self.client.table("profiles").select("*").eq("id", row["author_id"]).limit(1).execute().data or []
        profile = self._map_community_profile(profile_rows[0] if profile_rows else {"id": row["author_id"], "name": "Plant Lover", "username": f"grower-{row['author_id'][:8]}"})
        return CommunityComment(
            id=UUID(row["id"]),
            post_id=UUID(row["post_id"]),
            author=profile,
            body=row["body"],
            created_at=datetime.fromisoformat(row["created_at"].replace("Z", "+00:00")),
            is_owner=row["author_id"] == viewer_user_id,
            updated_at=datetime.fromisoformat(row["updated_at"].replace("Z", "+00:00")) if row.get("updated_at") else None,
        )

    def _map_community_profile(self, row: dict[str, Any]) -> CommunityProfile:
        return CommunityProfile(
            id=UUID(str(row["id"])),
            username=row.get("username") or f"grower-{str(row['id'])[:8]}",
            display_name=row.get("name") or "Plant Lover",
            avatar_url=row.get("avatar_url"),
            bio=row.get("bio"),
        )

    def _sanitize_username(self, value: str) -> str:
        cleaned = re.sub(r"[^a-z0-9_]+", "-", value.strip().lower()).strip("-")
        return cleaned[:30] or "grower"

    def _build_username(self, user_id: str, user_email: str | None) -> str:
        base = self._sanitize_username((user_email or "grower").split("@")[0])
        return f"{base}-{user_id[:8]}"[:30]

    def _build_display_name(self, user_email: str | None) -> str:
        if not user_email:
            return "Plant Lover"
        return user_email.split("@")[0].replace(".", " ").replace("_", " ").title()[:80]
