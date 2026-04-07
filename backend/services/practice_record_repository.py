# services/practice_record_repository.py
from typing import Optional, List, Dict, Any
from datetime import datetime, timedelta
from sqlalchemy import func as sa_func
from sqlalchemy.sql import text
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

    def get_history(
        self,
        page: int = 1,
        page_size: int = 10,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Paginated list of past practice records with task image URL joined,
        sorted by most recent. Supports optional date-range filtering.
        """
        db = SessionLocal()
        try:
            query = (
                "SELECT r.id, r.task_id, r.user_id, r.user_audio_url, "
                "r.asr_text, r.ai_feedback, r.relevance_score, r.fluency_score, "
                "r.created_at, t.image_url, t.difficulty "
                "FROM user_practice_record r "
                "LEFT JOIN image_practice_task t ON r.task_id = t.id"
            )
            count_query = (
                "SELECT COUNT(*) as total "
                "FROM user_practice_record r"
            )
            params: Dict[str, Any] = {}

            where_clauses = []
            if start_date:
                where_clauses.append("r.created_at >= :start_date")
                params["start_date"] = start_date
            if end_date:
                where_clauses.append("r.created_at <= :end_date")
                params["end_date"] = end_date

            if where_clauses:
                where_str = " WHERE " + " AND ".join(where_clauses)
                query += where_str
                count_query += where_str

            # Get total count
            total = db.execute(text(count_query), params).scalar()

            # Add ordering and pagination
            query += " ORDER BY r.created_at DESC LIMIT :limit OFFSET :offset"
            params["limit"] = page_size
            params["offset"] = (page - 1) * page_size

            rows = db.execute(text(query), params).mappings().all()
            records = [dict(row) for row in rows]

            return {
                "records": records,
                "total": total,
                "page": page,
                "page_size": page_size,
                "total_pages": (total + page_size - 1) // page_size if total else 0,
            }
        finally:
            db.close()

    def get_stats(self, trend_count: int = 20) -> Dict[str, Any]:
        """
        Aggregated stats: total sessions, average relevance/fluency scores,
        score trend over last N sessions, best scores, current streak.
        """
        db = SessionLocal()
        try:
            # Total sessions
            total_sessions = db.execute(
                text("SELECT COUNT(*) FROM user_practice_record")
            ).scalar() or 0

            if total_sessions == 0:
                return {
                    "total_sessions": 0,
                    "avg_relevance_score": 0,
                    "avg_fluency_score": 0,
                    "best_relevance_score": 0,
                    "best_fluency_score": 0,
                    "score_trend": [],
                    "current_streak": 0,
                }

            # Average scores
            avg_row = db.execute(
                text(
                    "SELECT "
                    "ROUND(AVG(relevance_score), 1) as avg_rel, "
                    "ROUND(AVG(fluency_score), 1) as avg_flu "
                    "FROM user_practice_record "
                    "WHERE relevance_score IS NOT NULL AND fluency_score IS NOT NULL"
                )
            ).mappings().first()
            avg_relevance = float(avg_row["avg_rel"]) if avg_row and avg_row["avg_rel"] else 0
            avg_fluency = float(avg_row["avg_flu"]) if avg_row and avg_row["avg_flu"] else 0

            # Best scores
            best_row = db.execute(
                text(
                    "SELECT "
                    "MAX(relevance_score) as best_rel, "
                    "MAX(fluency_score) as best_flu "
                    "FROM user_practice_record"
                )
            ).mappings().first()
            best_relevance = int(best_row["best_rel"]) if best_row and best_row["best_rel"] else 0
            best_fluency = int(best_row["best_flu"]) if best_row and best_row["best_flu"] else 0

            # Score trend (last N sessions)
            trend_rows = db.execute(
                text(
                    "SELECT relevance_score, fluency_score, created_at "
                    "FROM user_practice_record "
                    "WHERE relevance_score IS NOT NULL AND fluency_score IS NOT NULL "
                    "ORDER BY created_at DESC LIMIT :limit"
                ),
                {"limit": trend_count},
            ).mappings().all()
            # Reverse so oldest is first for charting
            score_trend = [
                {
                    "relevance_score": row["relevance_score"],
                    "fluency_score": row["fluency_score"],
                    "created_at": row["created_at"].isoformat() if hasattr(row["created_at"], "isoformat") else str(row["created_at"]),
                }
                for row in reversed(list(trend_rows))
            ]

            # Current streak (consecutive days with at least one practice)
            distinct_days = db.execute(
                text(
                    "SELECT DISTINCT DATE(created_at) as practice_date "
                    "FROM user_practice_record "
                    "ORDER BY practice_date DESC"
                )
            ).fetchall()

            current_streak = 0
            if distinct_days:
                today = datetime.utcnow().date()
                expected = today
                for row in distinct_days:
                    day = row[0]
                    if hasattr(day, "date"):
                        day = day.date()
                    if day == expected:
                        current_streak += 1
                        expected -= timedelta(days=1)
                    elif day == expected - timedelta(days=1):
                        # Allow starting streak from yesterday if no practice today yet
                        if current_streak == 0:
                            expected = day
                            current_streak = 1
                            expected -= timedelta(days=1)
                        else:
                            break
                    else:
                        break

            return {
                "total_sessions": total_sessions,
                "avg_relevance_score": avg_relevance,
                "avg_fluency_score": avg_fluency,
                "best_relevance_score": best_relevance,
                "best_fluency_score": best_fluency,
                "score_trend": score_trend,
                "current_streak": current_streak,
            }
        finally:
            db.close()
