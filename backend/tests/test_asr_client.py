"""Tests for models/asr_client.py – ASRClient."""

import os
from unittest.mock import patch, MagicMock

import pytest

from models.asr_client import ASRClient


# ---------------------------------------------------------------------------
# __init__
# ---------------------------------------------------------------------------

class TestASRClientInit:
    def test_init_with_valid_key(self):
        """ASRClient() succeeds when DASHSCOPE_API_KEY is set (via conftest)."""
        client = ASRClient()
        assert client.api_key == os.getenv("DASHSCOPE_API_KEY")

    def test_init_without_key(self):
        """ASRClient() raises RuntimeError when the key is missing."""
        with patch("models.asr_client.os.getenv", return_value=None):
            with pytest.raises(RuntimeError, match="DASHSCOPE_API_KEY not found"):
                ASRClient()


# ---------------------------------------------------------------------------
# speech_to_text
# ---------------------------------------------------------------------------

class TestSpeechToText:
    def test_speech_to_text_file_not_found(self):
        """Raise FileNotFoundError for a non-existent audio path."""
        client = ASRClient()
        with pytest.raises(FileNotFoundError, match="Audio file not found"):
            client.speech_to_text("/tmp/this_audio_does_not_exist.wav")

    @patch("models.asr_client.dashscope.MultiModalConversation.call")
    def test_speech_to_text_success(self, mock_call, tmp_path):
        """Happy path: API returns status 200 with expected text."""
        audio_file = tmp_path / "test.wav"
        audio_file.write_bytes(b"\x00")

        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.output = {
            "choices": [
                {
                    "message": {
                        "content": [
                            {"text": "hello"},
                            {"text": "world"},
                        ]
                    }
                }
            ]
        }
        mock_call.return_value = mock_response

        client = ASRClient()
        result = client.speech_to_text(str(audio_file))

        assert result == "hello world"
        mock_call.assert_called_once()

    @patch("models.asr_client.dashscope.MultiModalConversation.call")
    def test_speech_to_text_api_failure(self, mock_call, tmp_path):
        """RuntimeError when the API returns a non-200 status code."""
        audio_file = tmp_path / "test.wav"
        audio_file.write_bytes(b"\x00")

        mock_response = MagicMock()
        mock_response.status_code = 500
        mock_call.return_value = mock_response

        client = ASRClient()
        with pytest.raises(RuntimeError, match="ASR failed"):
            client.speech_to_text(str(audio_file))


# ---------------------------------------------------------------------------
# _extract_text
# ---------------------------------------------------------------------------

class TestExtractText:
    def test_extract_text_success(self):
        """Correctly extracts and joins text fragments from the response."""
        mock_response = MagicMock()
        mock_response.output = {
            "choices": [
                {
                    "message": {
                        "content": [
                            {"text": "The quick"},
                            {"text": "brown fox"},
                        ]
                    }
                }
            ]
        }

        client = ASRClient()
        result = client._extract_text(mock_response)
        assert result == "The quick brown fox"

    def test_extract_text_failure(self):
        """RuntimeError when the response structure is unexpected."""
        mock_response = MagicMock()
        mock_response.output = None

        client = ASRClient()
        with pytest.raises(RuntimeError, match="Parse ASR result failed"):
            client._extract_text(mock_response)
