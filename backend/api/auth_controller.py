from fastapi import APIRouter, HTTPException, Depends
from schemas.auth import (
    RegisterRequest,
    LoginRequest,
    RefreshRequest,
)
from services.user_service import UserService
from services.auth_service import AuthService
from services.subscription_service import SubscriptionService
from middleware.auth_middleware import get_current_user

router = APIRouter()


@router.post("/register", status_code=201)
def register(req: RegisterRequest):
    """Register a new user."""
    if not req.email or not req.password:
        raise HTTPException(status_code=400, detail="Email and password are required")

    if len(req.password) < 6:
        raise HTTPException(
            status_code=400, detail="Password must be at least 6 characters"
        )

    user_service = UserService()
    try:
        user = user_service.create_user(
            email=req.email, password=req.password, nickname=req.nickname
        )
    except ValueError as e:
        raise HTTPException(status_code=409, detail=str(e))

    access_token = AuthService.create_access_token(user.id, user.email)
    refresh_token = AuthService.create_refresh_token(user.id)

    return {
        "user": {
            "id": user.id,
            "email": user.email,
            "nickname": user.nickname,
        },
        "access_token": access_token,
        "refresh_token": refresh_token,
    }


@router.post("/login")
def login(req: LoginRequest):
    """Login with email and password."""
    user_service = UserService()
    user = user_service.get_user_by_email(req.email)

    if not user or not AuthService.verify_password(req.password, user.password_hash):
        raise HTTPException(status_code=401, detail="Invalid email or password")

    if not user.is_active:
        raise HTTPException(status_code=403, detail="Account is deactivated")

    access_token = AuthService.create_access_token(user.id, user.email)
    refresh_token = AuthService.create_refresh_token(user.id)

    return {
        "user": {
            "id": user.id,
            "email": user.email,
            "nickname": user.nickname,
        },
        "access_token": access_token,
        "refresh_token": refresh_token,
    }


@router.post("/refresh")
def refresh_token(req: RefreshRequest):
    """Refresh access token using refresh token."""
    payload = AuthService.verify_refresh_token(req.refresh_token)
    if not payload:
        raise HTTPException(status_code=401, detail="Invalid or expired refresh token")

    user_service = UserService()
    user = user_service.get_user_by_id(payload["sub"])
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    access_token = AuthService.create_access_token(user.id, user.email)
    return {"access_token": access_token}


@router.get("/me")
def get_me(current_user: dict = Depends(get_current_user)):
    """Get current user profile with subscription info."""
    user_service = UserService()
    user = user_service.get_user_by_id(current_user["sub"])

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    sub_service = SubscriptionService()
    subscription = sub_service.get_user_subscription(user.id)

    return {
        "id": user.id,
        "email": user.email,
        "nickname": user.nickname,
        "avatar_url": user.avatar_url,
        "subscription": subscription,
    }
