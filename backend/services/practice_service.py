from fastapi import File, UploadFile
from typing import Dict
from models.asr_client import ASRClient
from models.qwen_client import QwenClient
from services.practice_record_repository import PracticeRecordRepository
import os
import uuid
import tempfile
from services.oss_client import OSSClient

class PracticeService:

    def __init__(self):
        self.asr_client = ASRClient()
        self.qwen_client = QwenClient()
        self.oss_client = OSSClient()

    def submit_practice(self, task, audio_file: UploadFile = File(...)):

        audio_path_obj = self.save_recording(audio_file)

        # 1. ASR
        asr_text = self.asr_client.speech_to_text(audio_path_obj["local_path"])
        # 记得 ASR 完成后可以删除临时文件
        print(audio_path_obj["local_path"])
        # os.remove(audio_path_obj["local_path"])

        # 2. 构造 prompt
        # 3. 调用 LLM
        result = self.qwen_client.evaluate_practice(
            semantic_plan=task["semantic_plan"],
            standard_answer=task["standard_answer"],
            user_text=asr_text
        )

        # 4. 存数据库
        repo = PracticeRecordRepository()
        practice_record = repo.save_record(
            task_id=task["id"],
            asr_text=asr_text,
            ai_feedback=result,
            relevance_score=result["relevance_score"],
            fluency_score=result["fluency_score"],
            user_audio_url=audio_path_obj["audio_url"]
        )

        return practice_record


    def save_recording(self, audio_file: UploadFile) -> Dict[str, str]:
        """
        1. 将录音文件上传到 OSS
        2. 同时保存一个本地临时文件（用于 ASR）
        返回：
        {
          "audio_url": OSS 公网 URL,
          "local_path": 本地文件路径
        }
        """

        # 1️⃣ 读取音频字节
        audio_bytes = audio_file.file.read()

        # 2️⃣ 生成文件名
        suffix = os.path.splitext(audio_file.filename)[1] or ".wav"
        object_name = f"user-audio/{uuid.uuid4().hex}{suffix}"

        # 3️⃣ 上传到 OSS
        audio_url = self.oss_client.upload_bytes(
            object_name=object_name,
            data=audio_bytes,
            content_type=audio_file.content_type
        )

        # 4️⃣ 保存为本地临时文件（给 ASR 用）
        with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
            tmp.write(audio_bytes)
            local_path = tmp.name

        return {
            "audio_url": audio_url,
            "local_path": local_path
        }