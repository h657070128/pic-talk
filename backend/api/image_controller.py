from fastapi import APIRouter
from services.image_task_service import ImageTaskService
from schemas.image_task import ImageTaskRequest

router = APIRouter()

@router.get("/generate")
def generate_image_task():
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
def get_random_task():
    """
    获取随机任务
    """
    service = ImageTaskService()
    result = service.get_random_task()
    return result