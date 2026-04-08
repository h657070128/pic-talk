from pydantic import BaseModel
from typing import Optional


class CreateOrderRequest(BaseModel):
    plan_id: int
    payment_method: str = "wechat"


class PlanResponse(BaseModel):
    id: int
    name: str
    display_name: str
    price_cents: int
    duration_days: int
    price_display: str
    per_month_display: str


class SubscriptionResponse(BaseModel):
    plan_name: str
    display_name: str
    status: str
    start_date: str
    end_date: str


class OrderResponse(BaseModel):
    order_id: str
    payment_url: Optional[str] = None
    qr_code_url: Optional[str] = None
    amount_cents: int
    status: str
