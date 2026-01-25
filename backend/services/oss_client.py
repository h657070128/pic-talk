# services/oss_client.py
import oss2
import requests
import uuid
import os
from typing import Optional
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class OSSClient:

    def __init__(self):
        auth = oss2.Auth(
            os.getenv("OSS_ACCESS_KEY_ID"),
            os.getenv("OSS_ACCESS_KEY_SECRET")
        )
        self.bucket = oss2.Bucket(
            auth,
            os.getenv("OSS_ENDPOINT"),
            os.getenv("OSS_BUCKET_NAME")
        )
        self.public_base_url = os.getenv("OSS_PUBLIC_BASE_URL")

    def upload_image_from_url(self, image_url: str) -> str:
        # 1. 下载图片
        response = requests.get(image_url)
        response.raise_for_status()

        image_bytes = response.content

        # 2. 生成 OSS 路径
        object_name = f"generated-images/{uuid.uuid4().hex}.png"

        # 3. 上传
        self.bucket.put_object(object_name, image_bytes)

        # 4. 返回公网 URL
        return f"{self.public_base_url}/{object_name}"


    def upload_bytes(
        self,
        object_name: str,
        data: bytes,
        content_type: Optional[str] = None
    ) -> str:
        headers = {}
        if content_type:
            headers["Content-Type"] = content_type

        self.bucket.put_object(object_name, data, headers=headers)
        return f"{self.public_base_url}/{object_name}"