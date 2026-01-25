import os
import dashscope
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class ASRClient:
    """
    使用 通义千问3-ASR-Flash 做语音识别
    """

    def __init__(self):
        # 北京地域（国内默认）
        dashscope.base_http_api_url = "https://dashscope.aliyuncs.com/api/v1"

        api_key = os.getenv("DASHSCOPE_API_KEY")
        if not api_key:
            raise RuntimeError("DASHSCOPE_API_KEY not found in environment")

        self.api_key = api_key

    def speech_to_text(self, audio_path: str) -> str:
        """
        本地音频文件 → 文字

        audio_path: ./test_audio.wav
        return: 识别文本
        """

        if not os.path.exists(audio_path):
            raise FileNotFoundError(f"Audio file not found: {audio_path}")

        # 转成绝对路径（更稳）
        audio_path = os.path.abspath(audio_path)

        messages = [
            {
                "role": "system",
                "content": [{"text": "请将音频内容准确转写为文字"}]
            },
            {
                "role": "user",
                "content": [
                    {
                        "audio": f"file://{audio_path}"
                    }
                ]
            }
        ]

        response = dashscope.MultiModalConversation.call(
            api_key=self.api_key,
            model="qwen3-asr-flash",
            messages=messages,
            result_format="message",
            asr_options={
                "enable_itn": False
            }
        )

        if response.status_code != 200:
            raise RuntimeError(
                f"ASR failed: {response.status_code}, {response}"
            )

        return self._extract_text(response)

    def _extract_text(self, response) -> str:
        """
        从返回结构中提取文本
        """

        try:
            content = response.output["choices"][0]["message"]["content"]

            texts = []

            for item in content:
                if "text" in item:
                    texts.append(item["text"])

            return " ".join(texts).strip()

        except Exception as e:
            raise RuntimeError(f"Parse ASR result failed: {e}")
