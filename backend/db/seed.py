"""Seed script to initialize subscription plans."""
from db.database import SessionLocal, engine, Base
from db.subscription_plan import SubscriptionPlan
from db.user import User
from db.user_subscription import UserSubscription
from db.payment_record import PaymentRecord
from db.image_practice_task import ImagePracticeTask
from db.user_practice_record import UserPracticeRecord


def create_tables():
    """Create all database tables."""
    Base.metadata.create_all(bind=engine)
    print("All tables created successfully.")


def seed_plans():
    """Seed the subscription_plan table with default plans."""
    db = SessionLocal()
    try:
        # Check if plans already exist
        existing = db.query(SubscriptionPlan).count()
        if existing > 0:
            print(f"Subscription plans already seeded ({existing} plans found). Skipping.")
            return

        plans = [
            SubscriptionPlan(
                name="monthly",
                display_name="\u6708\u5ea6\u4f1a\u5458",
                price_cents=600,
                duration_days=30,
            ),
            SubscriptionPlan(
                name="quarterly",
                display_name="\u5b63\u5ea6\u4f1a\u5458",
                price_cents=1200,
                duration_days=90,
            ),
            SubscriptionPlan(
                name="yearly",
                display_name="\u5e74\u5ea6\u4f1a\u5458",
                price_cents=3900,
                duration_days=365,
            ),
        ]
        db.add_all(plans)
        db.commit()
        print("Subscription plans seeded successfully.")
    finally:
        db.close()


if __name__ == "__main__":
    create_tables()
    seed_plans()
