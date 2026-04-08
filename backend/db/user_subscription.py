from sqlalchemy import Column, BigInteger, String, Integer, DateTime, ForeignKey, Index
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from db.database import Base


class UserSubscription(Base):
    __tablename__ = "user_subscription"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    user_id = Column(BigInteger, ForeignKey("user.id"), nullable=False, index=True)
    plan_id = Column(BigInteger, ForeignKey("subscription_plan.id"), nullable=False)
    status = Column(String(32), nullable=False, default="active")
    start_date = Column(DateTime, nullable=False)
    end_date = Column(DateTime, nullable=False)
    payment_id = Column(String(128), nullable=True)
    amount_paid = Column(Integer, nullable=False)
    created_at = Column(DateTime, server_default=func.now())

    user = relationship("User", backref="subscriptions")
    plan = relationship("SubscriptionPlan")

    __table_args__ = (
        Index("idx_user_status", "user_id", "status"),
    )
