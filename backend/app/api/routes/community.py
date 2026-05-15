from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Response, status

from app.core.auth import CurrentUser, get_current_user
from app.core.deps import get_store
from app.models.schemas import (
    CommunityComment,
    CommunityCommentCreate,
    CommunityCommentUpdate,
    CommunityFeedResponse,
    CommunityLikeResponse,
    CommunityPost,
    CommunityPostCreate,
    CommunityPostUpdate,
    CommunityProfile,
    CommunityProfilePage,
    CommunityProfileUpdate,
)


router = APIRouter(prefix="/community")


@router.get("/feed", response_model=CommunityFeedResponse)
def get_feed(limit: int = 20, offset: int = 0, store=Depends(get_store), user: CurrentUser = Depends(get_current_user)) -> CommunityFeedResponse:
    return store.list_community_feed(user.id, user.email, limit=limit, offset=offset)


@router.post("/posts", response_model=CommunityPost, status_code=201)
def create_post(
    payload: CommunityPostCreate,
    store=Depends(get_store),
    user: CurrentUser = Depends(get_current_user),
) -> CommunityPost:
    return store.create_community_post(user.id, user.email, payload)


@router.patch("/posts/{post_id}", response_model=CommunityPost)
def update_post(
    post_id: UUID,
    payload: CommunityPostUpdate,
    store=Depends(get_store),
    user: CurrentUser = Depends(get_current_user),
) -> CommunityPost:
    try:
        return store.update_community_post(user.id, post_id, payload)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


@router.delete("/posts/{post_id}", status_code=204)
def delete_post(post_id: UUID, store=Depends(get_store), user: CurrentUser = Depends(get_current_user)) -> Response:
    try:
        store.delete_community_post(user.id, post_id)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.get("/posts/{post_id}/comments", response_model=list[CommunityComment])
def get_comments(post_id: UUID, store=Depends(get_store), user: CurrentUser = Depends(get_current_user)) -> list[CommunityComment]:
    return store.list_community_comments(user.id, user.email, post_id)


@router.post("/posts/{post_id}/comments", response_model=CommunityComment, status_code=201)
def create_comment(
    post_id: UUID,
    payload: CommunityCommentCreate,
    store=Depends(get_store),
    user: CurrentUser = Depends(get_current_user),
) -> CommunityComment:
    try:
        return store.create_community_comment(user.id, user.email, post_id, payload)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


@router.patch("/comments/{comment_id}", response_model=CommunityComment)
def update_comment(
    comment_id: UUID,
    payload: CommunityCommentUpdate,
    store=Depends(get_store),
    user: CurrentUser = Depends(get_current_user),
) -> CommunityComment:
    try:
        return store.update_community_comment(user.id, comment_id, payload)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


@router.delete("/comments/{comment_id}", status_code=204)
def delete_comment(comment_id: UUID, store=Depends(get_store), user: CurrentUser = Depends(get_current_user)) -> Response:
    try:
        store.delete_community_comment(user.id, comment_id)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.post("/posts/{post_id}/like", response_model=CommunityLikeResponse)
def like_post(post_id: UUID, store=Depends(get_store), user: CurrentUser = Depends(get_current_user)) -> CommunityLikeResponse:
    try:
        return store.toggle_community_like(user.id, user.email, post_id, liked=True)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


@router.delete("/posts/{post_id}/like", response_model=CommunityLikeResponse)
def unlike_post(post_id: UUID, store=Depends(get_store), user: CurrentUser = Depends(get_current_user)) -> CommunityLikeResponse:
    try:
        return store.toggle_community_like(user.id, user.email, post_id, liked=False)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


@router.get("/profile/me", response_model=CommunityProfile)
def get_my_profile(store=Depends(get_store), user: CurrentUser = Depends(get_current_user)) -> CommunityProfile:
    return store.get_or_create_community_profile(user.id, user.email)


@router.patch("/profile/me", response_model=CommunityProfile)
def update_my_profile(
    payload: CommunityProfileUpdate,
    store=Depends(get_store),
    user: CurrentUser = Depends(get_current_user),
) -> CommunityProfile:
    return store.update_community_profile(user.id, user.email, payload)


@router.get("/profiles/{username}", response_model=CommunityProfilePage)
def get_profile_page(username: str, limit: int = 20, offset: int = 0, store=Depends(get_store), user: CurrentUser = Depends(get_current_user)) -> CommunityProfilePage:
    page = store.get_community_profile_page(user.id, username, limit=limit, offset=offset)
    if page is None:
        raise HTTPException(status_code=404, detail="Profile not found")
    return page
