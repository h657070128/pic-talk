from sqlalchemy import Column, BigInteger, String, Text, DateTime, JSON
from sqlalchemy.sql import func
from db.database import Base


class ImagePracticeTask(Base):
    __tablename__ = "image_practice_task"

    id = Column(BigInteger, primary_key=True, index=True)
    semantic_plan = Column(JSON, nullable=False)
    image_url = Column(String(512), nullable=False)
    standard_answer = Column(Text, nullable=False)
    difficulty = Column(String(32), nullable=False)
    created_at = Column(DateTime, server_default=func.now())
