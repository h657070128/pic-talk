from fastapi import APIRouter, UploadFile, File, Form, HTTPException, Depends
from services.image_task_service import ImageTaskService
from services.speech_service import SpeechService
from services.evaluation_service import EvaluationService
from services.practice_service import PracticeService
from middleware.subscription_guard import check_daily_quota

router = APIRouter()

@router.post("/evaluate")
async def evaluate_practice(
    task_id: int = Form(...),
    audio_file: UploadFile = File(...),
    user: dict = Depends(check_daily_quota),
):
    """
    音频 → ASR → 文本分析
    """
    image_task_service = ImageTaskService()
    task = image_task_service.get_task_by_id(task_id)
    
    if not task:
        raise HTTPException(status_code=404, detail=f"Task with id {task_id} not found")

    practice_service = PracticeService()
    practice_record = practice_service.submit_practice(task, audio_file, user_id=user["sub"])

    return practice_record
