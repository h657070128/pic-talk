from models.qwen_client import QwenClient
from models.qwen_image_max_client import QwenImageMaxClient
from services.oss_client import OSSClient
from services.image_task_repository import ImageTaskRepository


class ImageTaskService:

    def __init__(self):
        self.qwen = QwenClient()
        self.qwen_image_max = QwenImageMaxClient()
        self.oss_client = OSSClient()

    def generate_image_task(self, difficulty_level: str):
        semantic_plan = self.qwen.generate_semantic_plan(difficulty_level)
        print(semantic_plan)

        # 1. 模型生成图片 URL
        temp_image_url = self.qwen_image_max.generate_image(semantic_plan)
        print(temp_image_url)
        # 2. 下载并上传 OSS
        oss_image_url = self.oss_client.upload_image_from_url(temp_image_url)
        print(oss_image_url)

        # 3. 生成标准答案
        standard_answer = self.qwen.generate_standard_answer(semantic_plan)
        print(standard_answer)

        # 4. 保存任务
        repo = ImageTaskRepository()
        task_id = repo.save_task(
            semantic_plan=semantic_plan,
            oss_image_url=oss_image_url,
            standard_answer=standard_answer,
            difficulty_level=difficulty_level
        )

        return {
            "semantic_plan": semantic_plan,
            "image_url": oss_image_url,
            "standard_answer": standard_answer
        }

    def get_random_task(self):
        repo = ImageTaskRepository()
        task = repo.get_random_task()
        return task

    def get_task_by_id(self, task_id: int):
        repo = ImageTaskRepository()
        task = repo.get_task_by_id(task_id)
        return task