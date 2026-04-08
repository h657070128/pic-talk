from fastapi import APIRouter, HTTPException, Depends
from schemas.auth import ProfileUpdateRequest
from services.user_service import UserService
from services.practice_record_repository import PracticeRecordRepository
from middleware.auth_middleware import get_current_user

router = APIRouter()


@router.put("/profile")
def update_profile(
    req: ProfileUpdateRequest,
    current_user: dict = Depends(get_current_user),
):
    """Update current user's profile."""
    user_service = UserService()
    user = user_service.update_profile(
        user_id=current_user["sub"],
        nickname=req.nickname,
        avatar_url=req.avatar_url,
    )
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return {
        "id": user.id,
        "email": user.email,
        "nickname": user.nickname,
        "avatar_url": user.avatar_url,
    }


@router.get("/practice-history")
def get_practice_history(
    limit: int = 20,
    offset: int = 0,
    current_user: dict = Depends(get_current_user),
):
    """Get paginated practice history for current user."""
    repo = PracticeRecordRepository()
    return repo.get_user_practice_history(
        user_id=current_user["sub"],
        limit=min(limit, 100),
        offset=offset,
    )
