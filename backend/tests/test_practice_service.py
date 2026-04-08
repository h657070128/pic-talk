"""Tests for services/practice_service.py"""
import os
from io import BytesIO
from unittest.mock import patch, MagicMock

from services.practice_service import PracticeService


class TestPracticeService:
    """Unit tests for PracticeService."""

    @patch("services.practice_service.PracticeRecordRepository")
    @patch("services.practice_service.OSSClient")
    @patch("services.practice_service.QwenClient")
    @patch("services.practice_service.ASRClient")
    def test_submit_practice(
        self, mock_asr_cls, mock_qwen_cls, mock_oss_cls, mock_repo_cls
    ):
        """Patch all dependencies, mock save_recording, verify full flow."""
        mock_asr = mock_asr_cls.return_value
        mock_qwen = mock_qwen_cls.return_value
        mock_repo = mock_repo_cls.return_value

        mock_asr.speech_to_text.return_value = "the child is playing"
        mock_qwen.evaluate_practice.return_value = {
            "relevance_score": 85,
            "fluency_score": 70,
            "summary": "Good job",
            "strengths": [],
            "issues": [],
            "suggestions": [],
        }
        mock_repo.save_record.return_value = {"id": 10, "asr_text": "the child is playing"}

        mock_audio = MagicMock()

        task = {
            "id": 1,
            "semantic_plan": {"scene": "park"},
            "standard_answer": "A child is playing in the park.",
        }

        service = PracticeService()

        with patch.object(
            service,
            "save_recording",
            return_value={
                "audio_url": "https://oss.example.com/audio.wav",
                "local_path": "/tmp/fake_audio.wav",
            },
        ):
            result = service.submit_practice(task, mock_audio)

        mock_asr.speech_to_text.assert_called_once_with("/tmp/fake_audio.wav")

        mock_qwen.evaluate_practice.assert_called_once_with(
            semantic_plan=task["semantic_plan"],
            standard_answer=task["standard_answer"],
            user_text="the child is playing",
        )

        mock_repo.save_record.assert_called_once()
        call_kwargs = mock_repo.save_record.call_args[1]
        assert call_kwargs["task_id"] == 1
        assert call_kwargs["asr_text"] == "the child is playing"
        assert call_kwargs["relevance_score"] == 85
        assert call_kwargs["fluency_score"] == 70
        assert call_kwargs["user_audio_url"] == "https://oss.example.com/audio.wav"

        assert result == {"id": 10, "asr_text": "the child is playing"}

    @patch("services.practice_service.OSSClient")
    @patch("services.practice_service.QwenClient")
    @patch("services.practice_service.ASRClient")
    def test_save_recording(self, mock_asr_cls, mock_qwen_cls, mock_oss_cls):
        """Create a mock UploadFile with BytesIO content, verify dict keys."""
        mock_oss = mock_oss_cls.return_value
        mock_oss.upload_bytes.return_value = "https://oss.example.com/user-audio/abc.wav"

        service = PracticeService()

        audio_content = b"fake audio bytes for testing"
        mock_audio = MagicMock()
        mock_audio.file = BytesIO(audio_content)
        mock_audio.filename = "test_recording.wav"
        mock_audio.content_type = "audio/wav"

        result = service.save_recording(mock_audio)

        assert "audio_url" in result
        assert "local_path" in result
        assert result["audio_url"] == "https://oss.example.com/user-audio/abc.wav"
        assert os.path.exists(result["local_path"])

        with open(result["local_path"], "rb") as f:
            assert f.read() == audio_content

        os.unlink(result["local_path"])

    @patch("services.practice_service.OSSClient")
    @patch("services.practice_service.QwenClient")
    @patch("services.practice_service.ASRClient")
    def test_save_recording_wav_extension(
        self, mock_asr_cls, mock_qwen_cls, mock_oss_cls
    ):
        """Verify .wav suffix is used when filename has .wav extension."""
        mock_oss = mock_oss_cls.return_value
        mock_oss.upload_bytes.return_value = "https://oss.example.com/audio.wav"

        service = PracticeService()

        mock_audio = MagicMock()
        mock_audio.file = BytesIO(b"audio data")
        mock_audio.filename = "my_recording.wav"
        mock_audio.content_type = "audio/wav"

        result = service.save_recording(mock_audio)

        assert result["local_path"].endswith(".wav")

        call_kwargs = mock_oss.upload_bytes.call_args[1]
        assert call_kwargs["object_name"].startswith("user-audio/")
        assert call_kwargs["object_name"].endswith(".wav")

        os.unlink(result["local_path"])

    @patch("services.practice_service.OSSClient")
    @patch("services.practice_service.QwenClient")
    @patch("services.practice_service.ASRClient")
    def test_save_recording_default_extension(
        self, mock_asr_cls, mock_qwen_cls, mock_oss_cls
    ):
        """Verify .wav is used as default when filename has no extension."""
        mock_oss = mock_oss_cls.return_value
        mock_oss.upload_bytes.return_value = "https://oss.example.com/audio.wav"

        service = PracticeService()

        mock_audio = MagicMock()
        mock_audio.file = BytesIO(b"audio data")
        mock_audio.filename = "noextension"
        mock_audio.content_type = "audio/wav"

        result = service.save_recording(mock_audio)

        assert result["local_path"].endswith(".wav")

        call_kwargs = mock_oss.upload_bytes.call_args[1]
        assert call_kwargs["object_name"].endswith(".wav")

        os.unlink(result["local_path"])
