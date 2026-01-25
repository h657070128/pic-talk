import os
import json
import base64
import requests
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

DASHSCOPE_API_KEY = os.getenv("DASHSCOPE_API_KEY")

if not DASHSCOPE_API_KEY:
    raise RuntimeError("DASHSCOPE_API_KEY is not set")

class QwenImageMaxClient:
    """
    Qwen-Image-Max 文生图（同步）
    API: /multimodal-generation/generation
    输入：语义计划 dict
    输出：image_base64
    """

    BASE_URL = (
        "https://dashscope.aliyuncs.com/api/v1/services/"
        "aigc/multimodal-generation/generation"
    )

    def __init__(self):
        self.api_key = DASHSCOPE_API_KEY
        if not self.api_key:
            raise RuntimeError("DASHSCOPE_API_KEY not set")

        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }


    def generate_image(self, semantic_plan: dict, size: str = "1024*1024") -> str:
        """
        语义计划 → image prompt → image(base64)
        """
        image_prompt = f"""
请根据以下图片语义计划生成一张真实风格的教学图片：

{semantic_plan}

图片要求：
- 真实照片风格
- 构图清晰，主体突出
- 画面元素不要过多
- 不要出现任何文字、标志或水印
- 适合英语学习者进行“看图说话”

"""
        return self._generate_image_from_prompt(image_prompt, size)


    def _generate_image_from_prompt(self, prompt: str, size: str) -> str:
        """
        调用 qwen-image-max，同步生成图片
        """
        payload = {
            "model": "qwen-image-max",
            "input": {
                "messages": [
                    {
                        "role": "user",
                        "content": [
                            {"type": "text", "text": prompt}
                        ]
                    }
                ]
            },
            "parameters": {
                "size": size
            }
        }

        response = requests.post(
            self.BASE_URL,
            headers=self.headers,
            json=payload,
            timeout=60
        )
        response.raise_for_status()

        data = response.json()

        # qwen-image-max 返回在 output -> choices -> message -> content
        content = data["output"]["choices"][0]["message"]["content"]

        for item in content:
            if item["image"] is not None:
                return item["image"]

        raise RuntimeError("No image found in qwen-image-max response")

    @staticmethod
    def save_base64_image(image_base64: str, path: str):
        """
        可选：保存图片到本地
        """
        image_bytes = base64.b64decode(image_base64)
        with open(path, "wb") as f:
            f.write(image_bytes)
