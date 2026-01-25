# services/practice_record_repository.py
from typing import Optional
from db.database import SessionLocal
from db.user_practice_record import UserPracticeRecord

class PracticeRecordRepository:

    def save_record(
        self,
        task_id: int,
        asr_text: str,
        ai_feedback: dict,
        relevance_score: int,
        fluency_score: int,
        user_id: Optional[int] = None,
        user_audio_url: Optional[str] = None
    ) -> int:
        """
        保存一次用户练习记录
        """
        db = SessionLocal()
        try:
            record = UserPracticeRecord(
                task_id=task_id,
                user_id=user_id,
                user_audio_url=user_audio_url,
                asr_text=asr_text,
                ai_feedback=ai_feedback,
                relevance_score=relevance_score,
                fluency_score=fluency_score
            )
            db.add(record)
            db.commit()
            db.refresh(record)
            return record
        finally:
            db.close()
