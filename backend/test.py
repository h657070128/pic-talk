from models.asr_client import ASRClient


if __name__ == "__main__":
    asr = ASRClient()

    text = asr.speech_to_text("test_audio.wav")

    print("====== ASR RESULT ======")
    print(text)
