"""Tests for services/speech_service.py"""
import pytest
from unittest.mock import patch, MagicMock

from services.speech_service import SpeechService


class TestSpeechService:
    """Unit tests for SpeechService."""

    @patch("services.speech_service.ASRClient")
    def test_init(self, mock_asr_cls):
        """Patch ASRClient, verify self.asr is set."""
        svc = SpeechService()
        mock_asr_cls.assert_called_once()
        assert svc.asr is mock_asr_cls.return_value

    @patch("services.speech_service.ASRClient")
    @pytest.mark.asyncio
    async def test_transcribe(self, mock_asr_cls):
        """Patch ASRClient transcribe method, verify it's called and result returned."""
        mock_asr_instance = mock_asr_cls.return_value
        mock_asr_instance.transcribe.return_value = "hello world"

        svc = SpeechService()
        mock_audio_file = MagicMock()

        result = await svc.transcribe(mock_audio_file)

        mock_asr_instance.transcribe.assert_called_once_with(mock_audio_file)
        assert result == "hello world"
