"""Tests for models/qwen_image_max_client.py – QwenImageMaxClient."""

import base64
from unittest.mock import patch, MagicMock

import pytest
import requests as requests_lib

from models.qwen_image_max_client import QwenImageMaxClient


# ---------------------------------------------------------------------------
# __init__
# ---------------------------------------------------------------------------

class TestInit:
    def test_init(self):
        """api_key and headers are set from the environment variable."""
        client = QwenImageMaxClient()
        assert client.api_key is not None
        assert "Authorization" in client.headers
        assert client.headers["Content-Type"] == "application/json"


# ---------------------------------------------------------------------------
# generate_image
# ---------------------------------------------------------------------------

class TestGenerateImage:
    def test_generate_image_success(self):
        """Returns the URL/base64 string from _generate_image_from_prompt."""
        expected_url = "https://example.com/image.png"

        with patch.object(
            QwenImageMaxClient,
            "_generate_image_from_prompt",
            return_value=expected_url,
        ) as mock_gen:
            client = QwenImageMaxClient()
            result = client.generate_image({"scene": "park"}, size="512*512")

        assert result == expected_url
        mock_gen.assert_called_once()


# ---------------------------------------------------------------------------
# _generate_image_from_prompt
# ---------------------------------------------------------------------------

class TestGenerateImageFromPrompt:
    @patch("models.qwen_image_max_client.requests.post")
    def test_generate_image_from_prompt_success(self, mock_post):
        """Returns the image URL when the API response is well-formed."""
        mock_response = MagicMock()
        mock_response.raise_for_status = MagicMock()
        mock_response.json.return_value = {
            "output": {
                "choices": [
                    {
                        "message": {
                            "content": [
                                {"image": "https://example.com/result.png"}
                            ]
                        }
                    }
                ]
            }
        }
        mock_post.return_value = mock_response

        client = QwenImageMaxClient()
        result = client._generate_image_from_prompt("draw a cat", "1024*1024")

        assert result == "https://example.com/result.png"
        mock_post.assert_called_once()

    @patch("models.qwen_image_max_client.requests.post")
    def test_generate_image_from_prompt_no_image(self, mock_post):
        """RuntimeError when no image field is found in the response."""
        mock_response = MagicMock()
        mock_response.raise_for_status = MagicMock()
        mock_response.json.return_value = {
            "output": {
                "choices": [
                    {
                        "message": {
                            "content": [
                                {"image": None}
                            ]
                        }
                    }
                ]
            }
        }
        mock_post.return_value = mock_response

        client = QwenImageMaxClient()
        with pytest.raises(RuntimeError, match="No image found"):
            client._generate_image_from_prompt("draw a cat", "1024*1024")

    @patch("models.qwen_image_max_client.requests.post")
    def test_generate_image_from_prompt_http_error(self, mock_post):
        """HTTP errors from requests propagate to the caller."""
        mock_post.side_effect = requests_lib.exceptions.ConnectionError("timeout")

        client = QwenImageMaxClient()
        with pytest.raises(requests_lib.exceptions.ConnectionError):
            client._generate_image_from_prompt("draw a cat", "1024*1024")


# ---------------------------------------------------------------------------
# save_base64_image (static method)
# ---------------------------------------------------------------------------

class TestSaveBase64Image:
    def test_save_base64_image(self, tmp_path):
        """Encodes known bytes to base64, saves via static method, and verifies."""
        original_bytes = b"fake image content for testing"
        encoded = base64.b64encode(original_bytes).decode("utf-8")

        output_path = tmp_path / "output.png"
        QwenImageMaxClient.save_base64_image(encoded, str(output_path))

        assert output_path.exists()
        assert output_path.read_bytes() == original_bytes
