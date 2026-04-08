from typing import Optional
from datetime import datetime, timezone
from sqlalchemy import and_
from db.database import SessionLocal
from db.subscription_plan import SubscriptionPlan
from db.user_subscription import UserSubscription
from db.payment_record import PaymentRecord


class SubscriptionRepository:

    def get_active_plans(self) -> list:
        """Return all active subscription plans."""
        db = SessionLocal()
        try:
            plans = db.query(SubscriptionPlan).filter(
                SubscriptionPlan.is_active == True
            ).all()
            return [
                {
                    "id": p.id,
                    "name": p.name,
                    "display_name": p.display_name,
                    "price_cents": p.price_cents,
                    "duration_days": p.duration_days,
                }
                for p in plans
            ]
        finally:
            db.close()

    def get_plan_by_id(self, plan_id: int) -> Optional[dict]:
        """Return a single plan by ID."""
        db = SessionLocal()
        try:
            p = db.query(SubscriptionPlan).filter(SubscriptionPlan.id == plan_id).first()
            if not p:
                return None
            return {
                "id": p.id,
                "name": p.name,
                "display_name": p.display_name,
                "price_cents": p.price_cents,
                "duration_days": p.duration_days,
            }
        finally:
            db.close()

    def get_active_subscription(self, user_id: int) -> Optional[dict]:
        """Return the user's current active subscription, or None."""
        db = SessionLocal()
        try:
            now = datetime.now(timezone.utc)
            sub = (
                db.query(UserSubscription)
                .filter(
                    and_(
                        UserSubscription.user_id == user_id,
                        UserSubscription.status == "active",
                        UserSubscription.end_date > now,
                    )
                )
                .order_by(UserSubscription.end_date.desc())
                .first()
            )
            if not sub:
                return None
            plan = db.query(SubscriptionPlan).filter(SubscriptionPlan.id == sub.plan_id).first()
            return {
                "id": sub.id,
                "plan_name": plan.name if plan else None,
                "display_name": plan.display_name if plan else None,
                "status": sub.status,
                "start_date": str(sub.start_date),
                "end_date": str(sub.end_date),
            }
        finally:
            db.close()

    def create_subscription(
        self,
        user_id: int,
        plan_id: int,
        start_date: datetime,
        end_date: datetime,
        amount_paid: int,
        payment_id: Optional[str] = None,
    ) -> dict:
        """Create a new user subscription record."""
        db = SessionLocal()
        try:
            sub = UserSubscription(
                user_id=user_id,
                plan_id=plan_id,
                status="active",
                start_date=start_date,
                end_date=end_date,
                payment_id=payment_id,
                amount_paid=amount_paid,
            )
            db.add(sub)
            db.commit()
            db.refresh(sub)
            return {
                "id": sub.id,
                "user_id": sub.user_id,
                "plan_id": sub.plan_id,
                "status": sub.status,
                "start_date": str(sub.start_date),
                "end_date": str(sub.end_date),
            }
        finally:
            db.close()

    def create_payment_record(
        self,
        user_id: int,
        amount_cents: int,
        payment_provider: str,
        subscription_id: Optional[int] = None,
        status: str = "pending",
    ) -> dict:
        """Create a payment record."""
        db = SessionLocal()
        try:
            record = PaymentRecord(
                user_id=user_id,
                subscription_id=subscription_id,
                payment_provider=payment_provider,
                amount_cents=amount_cents,
                status=status,
                paid_at=datetime.now(timezone.utc) if status == "success" else None,
            )
            db.add(record)
            db.commit()
            db.refresh(record)
            return {
                "id": record.id,
                "status": record.status,
            }
        finally:
            db.close()
