from datetime import date, datetime
from typing import Optional, List
from sqlalchemy import func, cast, Date
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
        user_audio_url: Optional[str] = None,
    ):
        db = SessionLocal()
        try:
            record = UserPracticeRecord(
                task_id=task_id,
                user_id=user_id,
                user_audio_url=user_audio_url,
                asr_text=asr_text,
                ai_feedback=ai_feedback,
                relevance_score=relevance_score,
                fluency_score=fluency_score,
            )
            db.add(record)
            db.commit()
            db.refresh(record)
            return record
        finally:
            db.close()

    def get_user_practice_history(self, user_id: int, limit: int = 20, offset: int = 0):
        """Get paginated practice history for a user."""
        db = SessionLocal()
        try:
            records = (
                db.query(UserPracticeRecord)
                .filter(UserPracticeRecord.user_id == user_id)
                .order_by(UserPracticeRecord.created_at.desc())
                .offset(offset)
                .limit(limit)
                .all()
            )
            total = (
                db.query(UserPracticeRecord)
                .filter(UserPracticeRecord.user_id == user_id)
                .count()
            )
            return {
                "records": [
                    {
                        "id": r.id,
                        "task_id": r.task_id,
                        "asr_text": r.asr_text,
                        "ai_feedback": r.ai_feedback,
                        "relevance_score": r.relevance_score,
                        "fluency_score": r.fluency_score,
                        "created_at": str(r.created_at),
                    }
                    for r in records
                ],
                "total": total,
                "limit": limit,
                "offset": offset,
            }
        finally:
            db.close()

    def get_today_practice_count(self, user_id: int) -> int:
        """Count practices for today for quota enforcement."""
        from sqlalchemy.sql import text
        from datetime import date

        db = SessionLocal()
        try:
            today = date.today().isoformat()
            result = db.execute(
                text(
                    "SELECT COUNT(*) as cnt FROM user_practice_record "
                    "WHERE user_id = :user_id AND DATE(created_at) = :today"
                ),
                {"user_id": user_id, "today": today},
            ).scalar()
            return result or 0
        finally:
            db.close()
