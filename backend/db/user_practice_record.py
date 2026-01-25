# models/user_practice_record.py
from sqlalchemy import Column, BigInteger, String, Text, DateTime, JSON, Integer, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from db.database import Base

class UserPracticeRecord(Base):
    __tablename__ = "user_practice_record"

    id = Column(BigInteger, primary_key=True, index=True)
    task_id = Column(BigInteger, ForeignKey("image_practice_task.id"), nullable=False, index=True)
    user_id = Column(BigInteger, nullable=True, index=True)
    user_audio_url = Column(String(512), nullable=True)
    asr_text = Column(Text, nullable=False)
    ai_feedback = Column(JSON, nullable=False)
    relevance_score = Column(Integer, nullable=True)
    fluency_score = Column(Integer, nullable=True)
    created_at = Column(DateTime, server_default=func.now())

    # Relationship to ImagePracticeTask
    task = relationship("ImagePracticeTask", backref="practice_records")
