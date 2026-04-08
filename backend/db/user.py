from sqlalchemy import Column, BigInteger, String, Boolean, DateTime
from sqlalchemy.sql import func
from db.database import Base


class User(Base):
    __tablename__ = "user"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    email = Column(String(255), nullable=False, unique=True, index=True)
    password_hash = Column(String(255), nullable=False)
    nickname = Column(String(64), nullable=True)
    avatar_url = Column(String(512), nullable=True)
    is_active = Column(Boolean, nullable=False, default=True)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())
