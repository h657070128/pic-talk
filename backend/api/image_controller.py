from fastapi import APIRouter, Depends
from services.image_task_service import ImageTaskService
from schemas.image_task import ImageTaskRequest
from middleware.subscription_guard import require_subscription, check_daily_quota

router = APIRouter()

@router.get("/generate")
def generate_image_task(user: dict = Depends(require_subscription)):
    """
    生成：
    - 图片语义计划
    - 图片（mock）
    - 标准答案
    """
    service = ImageTaskService()
    result = service.generate_image_task("beginner")
    return result

@router.get("/get_random_task")
def get_random_task(user: dict = Depends(check_daily_quota)):
    """
    获取随机任务
    """
    service = ImageTaskService()
    result = service.get_random_task()
    return result
