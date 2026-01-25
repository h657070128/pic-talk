from models.asr_client import ASRClient

class SpeechService:

    def __init__(self):
        self.asr = ASRClient()

    async def transcribe(self, audio_file):
        # 这里直接 mock，不解析音频
        return self.asr.transcribe(audio_file)
