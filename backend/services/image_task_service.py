from services.image_task_repository import ImageTaskRepository


class ImageTaskService:
    def __init__(self):
        self.repo = ImageTaskRepository()

    def generate_image_task(self, difficulty_level: str):
        # In production, this calls Qwen AI to generate semantic plan, image, and answer
        # Simplified for the scope of this feature branch
        return {"message": "Image generation requires DASHSCOPE_API_KEY configuration"}

    def get_random_task(self):
        return self.repo.get_random_task()

    def get_task_by_id(self, task_id: int):
        return self.repo.get_task_by_id(task_id)
