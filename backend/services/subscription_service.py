import os
import uuid
from datetime import datetime, timedelta, timezone
from typing import Optional
from db.database import SessionLocal
from db.subscription_plan import SubscriptionPlan
from db.user_subscription import UserSubscription
from db.payment_record import PaymentRecord
from dotenv import load_dotenv

load_dotenv()

PAYMENT_MODE = os.getenv("PAYMENT_MODE", "test")


class SubscriptionService:
    def get_plans(self) -> list:
        """Return all active subscription plans."""
        db = SessionLocal()
        try:
            plans = (
                db.query(SubscriptionPlan)
                .filter(SubscriptionPlan.is_active == True)
                .all()
            )
            result = []
            for p in plans:
                per_month = p.price_cents / (p.duration_days / 30)
                result.append(
                    {
                        "id": p.id,
                        "name": p.name,
                        "display_name": p.display_name,
                        "price_cents": p.price_cents,
                        "duration_days": p.duration_days,
                        "price_display": f"\u00a5{p.price_cents / 100:.0f}",
                        "per_month_display": f"\u00a5{per_month / 100:.1f}/\u6708",
                    }
                )
            return result
        finally:
            db.close()

    def get_user_subscription(self, user_id: int) -> Optional[dict]:
        """Return user's current active subscription, or None."""
        db = SessionLocal()
        try:
            sub = (
                db.query(UserSubscription)
                .filter(
                    UserSubscription.user_id == user_id,
                    UserSubscription.status == "active",
                    UserSubscription.end_date > datetime.now(timezone.utc),
                )
                .order_by(UserSubscription.end_date.desc())
                .first()
            )
            if not sub:
                return None
            plan = (
                db.query(SubscriptionPlan)
                .filter(SubscriptionPlan.id == sub.plan_id)
                .first()
            )
            return {
                "plan_name": plan.name if plan else "unknown",
                "display_name": plan.display_name if plan else "Unknown",
                "status": sub.status,
                "start_date": str(sub.start_date),
                "end_date": str(sub.end_date),
            }
        finally:
            db.close()

    def is_user_subscribed(self, user_id: int) -> bool:
        """Check if user has an active (non-expired) subscription."""
        return self.get_user_subscription(user_id) is not None

    def create_order(
        self, user_id: int, plan_id: int, payment_method: str = "wechat"
    ) -> dict:
        """
        Create a payment order for a subscription.
        In test mode, immediately activates the subscription.
        """
        db = SessionLocal()
        try:
            plan = (
                db.query(SubscriptionPlan)
                .filter(SubscriptionPlan.id == plan_id)
                .first()
            )
            if not plan:
                raise ValueError("Plan not found")

            order_id = f"ORD{datetime.now().strftime('%Y%m%d%H%M%S')}{uuid.uuid4().hex[:6].upper()}"

            payment = PaymentRecord(
                user_id=user_id,
                payment_provider=payment_method,
                provider_order_id=order_id,
                amount_cents=plan.price_cents,
                status="pending",
            )
            db.add(payment)
            db.commit()
            db.refresh(payment)

            if PAYMENT_MODE == "test":
                now = datetime.now(timezone.utc)

                existing = (
                    db.query(UserSubscription)
                    .filter(
                        UserSubscription.user_id == user_id,
                        UserSubscription.status == "active",
                        UserSubscription.end_date > now,
                    )
                    .first()
                )

                if existing:
                    existing.end_date = existing.end_date + timedelta(
                        days=plan.duration_days
                    )
                    existing.plan_id = plan.id
                    db.commit()
                    subscription = existing
                else:
                    subscription = UserSubscription(
                        user_id=user_id,
                        plan_id=plan.id,
                        status="active",
                        start_date=now,
                        end_date=now + timedelta(days=plan.duration_days),
                        payment_id=order_id,
                        amount_paid=plan.price_cents,
                    )
                    db.add(subscription)
                    db.commit()
                    db.refresh(subscription)

                payment.status = "success"
                payment.paid_at = now
                payment.subscription_id = subscription.id
                db.commit()

                return {
                    "order_id": order_id,
                    "amount_cents": plan.price_cents,
                    "status": "success",
                    "message": "Test mode: subscription activated immediately",
                }
            else:
                return {
                    "order_id": order_id,
                    "payment_url": f"weixin://wxpay/bizpayurl?order={order_id}",
                    "qr_code_url": None,
                    "amount_cents": plan.price_cents,
                    "status": "pending",
                }
        finally:
            db.close()

    def expire_subscriptions(self):
        """Batch job: mark subscriptions past end_date as 'expired'."""
        db = SessionLocal()
        try:
            now = datetime.now(timezone.utc)
            expired = (
                db.query(UserSubscription)
                .filter(
                    UserSubscription.status == "active",
                    UserSubscription.end_date <= now,
                )
                .all()
            )
            for sub in expired:
                sub.status = "expired"
            db.commit()
            return len(expired)
        finally:
            db.close()
