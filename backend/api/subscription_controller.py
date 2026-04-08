from fastapi import APIRouter, HTTPException, Depends
from schemas.subscription import CreateOrderRequest
from services.subscription_service import SubscriptionService
from middleware.auth_middleware import get_current_user

router = APIRouter()


@router.get("/plans")
def get_plans():
    """Return all active subscription plans (public)."""
    svc = SubscriptionService()
    return {"plans": svc.get_plans()}


@router.get("/my")
def get_my_subscription(current_user: dict = Depends(get_current_user)):
    """Return the current user's active subscription."""
    svc = SubscriptionService()
    subscription = svc.get_user_subscription(current_user["sub"])
    return {"subscription": subscription}


@router.post("/create-order")
def create_order(
    req: CreateOrderRequest,
    current_user: dict = Depends(get_current_user),
):
    """Create a payment order for a subscription plan."""
    svc = SubscriptionService()
    try:
        result = svc.create_order(
            user_id=current_user["sub"],
            plan_id=req.plan_id,
            payment_method=req.payment_method,
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    return result
