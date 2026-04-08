from sqlalchemy import Column, BigInteger, String, Integer, DateTime, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from db.database import Base


class PaymentRecord(Base):
    __tablename__ = "payment_record"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    user_id = Column(BigInteger, ForeignKey("user.id"), nullable=False)
    subscription_id = Column(BigInteger, ForeignKey("user_subscription.id"), nullable=True)
    payment_provider = Column(String(32), nullable=False)
    provider_order_id = Column(String(128), nullable=True)
    amount_cents = Column(Integer, nullable=False)
    status = Column(String(32), nullable=False, default="pending")
    paid_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())

    user = relationship("User")
    subscription = relationship("UserSubscription")
