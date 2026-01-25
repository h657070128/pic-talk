# services/image_task_repository.py
import json
from sqlalchemy.sql import text
from db.database import SessionLocal
from db.image_practice_task import ImagePracticeTask

class ImageTaskRepository:

    def save_task(
        self,
        semantic_plan: dict,
        oss_image_url: str,
        standard_answer: dict,
        difficulty_level: str
    ) -> int:
        db = SessionLocal()
        try:
            # Convert standard_answer dict to JSON string for Text column
            standard_answer_str = json.dumps(standard_answer, ensure_ascii=False)
            
            task = ImagePracticeTask(
                semantic_plan=semantic_plan,
                image_url=oss_image_url,
                standard_answer=standard_answer_str,
                difficulty=difficulty_level
            )
            db.add(task)
            db.commit()
            db.refresh(task)
            return task.id
        finally:
            db.close()

    def get_random_task(self):
        db = SessionLocal()
        try:
            result = db.execute(
                text("SELECT * FROM image_practice_task ORDER BY RAND() LIMIT 1")
            ).mappings().first()
            return dict(result) if result else None
        finally:
            db.close()

    def get_task_by_id(self, task_id: int):
        db = SessionLocal()
        try:
            result = db.execute(
                text("SELECT * FROM image_practice_task WHERE id = :task_id"),
                {"task_id": task_id}
            ).mappings().first()
            return dict(result) if result else None
        finally:
            db.close()
