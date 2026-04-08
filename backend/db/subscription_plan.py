from sqlalchemy import Column, BigInteger, String, Integer, Boolean, DateTime
from sqlalchemy.sql import func
from db.database import Base


class SubscriptionPlan(Base):
    __tablename__ = "subscription_plan"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    name = Column(String(32), nullable=False, unique=True)
    display_name = Column(String(64), nullable=False)
    price_cents = Column(Integer, nullable=False)
    duration_days = Column(Integer, nullable=False)
    is_active = Column(Boolean, nullable=False, default=True)
    created_at = Column(DateTime, server_default=func.now())
