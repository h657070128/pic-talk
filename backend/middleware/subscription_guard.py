from fastapi import Depends, HTTPException
from middleware.auth_middleware import get_current_user
from services.subscription_service import SubscriptionService
from services.practice_record_repository import PracticeRecordRepository


def require_subscription(user: dict = Depends(get_current_user)):
    """Raise 403 if user does not have an active subscription."""
    svc = SubscriptionService()
    if not svc.is_user_subscribed(user["sub"]):
        raise HTTPException(status_code=403, detail="Active subscription required")
    return user


def check_daily_quota(user: dict = Depends(get_current_user)):
    """
    For free-tier users: check if daily practice count < 3.
    Subscribed users pass through unconditionally.
    """
    svc = SubscriptionService()
    if svc.is_user_subscribed(user["sub"]):
        return user

    repo = PracticeRecordRepository()
    today_count = repo.get_today_practice_count(user["sub"])
    if today_count >= 3:
        raise HTTPException(
            status_code=429,
            detail="Daily free limit reached. Subscribe to continue.",
        )
    return user
