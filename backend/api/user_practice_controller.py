from typing import Optional
from fastapi import APIRouter, UploadFile, File, Form, HTTPException, Query
from services.image_task_service import ImageTaskService
from services.speech_service import SpeechService
from services.evaluation_service import EvaluationService
from services.practice_service import PracticeService
from services.practice_record_repository import PracticeRecordRepository

router = APIRouter()

@router.post("/evaluate")
async def evaluate_practice(
    task_id: int = Form(...),
    audio_file: UploadFile = File(...)
):
    """
    音频 → ASR → 文本分析
    """
    image_task_service = ImageTaskService()
    task = image_task_service.get_task_by_id(task_id)
    
    if not task:
        raise HTTPException(status_code=404, detail=f"Task with id {task_id} not found")

    practice_service = PracticeService()
    practice_record = practice_service.submit_practice(task, audio_file)

    return practice_record


@router.get("/history")
async def get_practice_history(
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(10, ge=1, le=50, description="Items per page"),
    start_date: Optional[str] = Query(None, description="Start date filter (YYYY-MM-DD)"),
    end_date: Optional[str] = Query(None, description="End date filter (YYYY-MM-DD)"),
):
    """
    Paginated list of past practice records with task image URL,
    sorted by most recent. Supports optional date-range filtering.
    """
    repo = PracticeRecordRepository()
    return repo.get_history(
        page=page,
        page_size=page_size,
        start_date=start_date,
        end_date=end_date,
    )


@router.get("/stats")
async def get_practice_stats(
    trend_count: int = Query(20, ge=1, le=100, description="Number of recent sessions for trend"),
):
    """
    Aggregated stats: total sessions, average relevance/fluency scores,
    score trend over last N sessions, best scores, current streak.
    """
    repo = PracticeRecordRepository()
    return repo.get_stats(trend_count=trend_count)
