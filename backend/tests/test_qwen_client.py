"""Tests for models/qwen_client.py – QwenClient."""

import json
from unittest.mock import patch, MagicMock

import httpx
import pytest

from models.qwen_client import QwenClient


# ---------------------------------------------------------------------------
# _chat
# ---------------------------------------------------------------------------

class TestChat:
    def test_chat_success(self):
        """_chat returns the content string when the API responds with valid JSON."""
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "choices": [
                {
                    "message": {
                        "content": "Hello from Qwen!"
                    }
                }
            ]
        }
        mock_response.raise_for_status = MagicMock()

        with patch.object(httpx.Client, "post", return_value=mock_response) as mock_post:
            client = QwenClient()
            result = client._chat([{"role": "user", "content": "hi"}])

        assert result == "Hello from Qwen!"
        mock_post.assert_called_once()

    def test_chat_http_error(self):
        """HTTPStatusError from the API propagates to the caller."""
        request = httpx.Request("POST", "https://example.com")
        response = httpx.Response(status_code=500, request=request)
        error = httpx.HTTPStatusError(
            "Server Error", request=request, response=response
        )

        with patch.object(httpx.Client, "post", side_effect=error):
            client = QwenClient()
            with pytest.raises(httpx.HTTPStatusError):
                client._chat([{"role": "user", "content": "hi"}])


# ---------------------------------------------------------------------------
# generate_semantic_plan
# ---------------------------------------------------------------------------

class TestGenerateSemanticPlan:
    def test_generate_semantic_plan_success(self):
        """Returns a parsed dict when _chat yields valid JSON."""
        plan = {
            "difficulty_level": "beginner",
            "scene": "a sunny park",
            "people": [{"role": "child", "appearance": "red hat", "emotion": "happy"}],
            "main_actions": ["feeding ducks"],
            "key_objects": ["bread", "ducks"],
            "background": "green trees",
        }

        with patch.object(QwenClient, "_chat", return_value=json.dumps(plan)):
            client = QwenClient()
            result = client.generate_semantic_plan("beginner")

        assert result == plan
        assert result["difficulty_level"] == "beginner"

    def test_generate_semantic_plan_invalid_json(self):
        """RuntimeError when _chat returns non-JSON text."""
        with patch.object(QwenClient, "_chat", return_value="not valid json {{{"):
            client = QwenClient()
            with pytest.raises(RuntimeError, match="Failed to parse semantic plan JSON"):
                client.generate_semantic_plan("beginner")


# ---------------------------------------------------------------------------
# generate_standard_answer
# ---------------------------------------------------------------------------

class TestGenerateStandardAnswer:
    def test_generate_standard_answer_success(self):
        """Returns a parsed dict when _chat yields valid JSON."""
        answer = {
            "key_facts": ["A child feeds ducks in the park."],
            "recommended_vocab": ["feed", "duck", "park"],
            "example_full_answer": "A young child is feeding ducks by the lake.",
        }
        semantic_plan = {"difficulty_level": "beginner", "scene": "park"}

        with patch.object(QwenClient, "_chat", return_value=json.dumps(answer)):
            client = QwenClient()
            result = client.generate_standard_answer(semantic_plan)

        assert result == answer
        assert "key_facts" in result

    def test_generate_standard_answer_invalid_json(self):
        """RuntimeError when _chat returns non-JSON text."""
        semantic_plan = {"difficulty_level": "beginner", "scene": "park"}

        with patch.object(QwenClient, "_chat", return_value="oops, not json!"):
            client = QwenClient()
            with pytest.raises(RuntimeError, match="Failed to parse standard answer JSON"):
                client.generate_standard_answer(semantic_plan)


# ---------------------------------------------------------------------------
# evaluate_practice
# ---------------------------------------------------------------------------

class TestEvaluatePractice:
    def test_evaluate_practice_success(self):
        """Returns a parsed dict with scores when _chat yields valid JSON."""
        evaluation = {
            "relevance_score": 85,
            "fluency_score": 72,
            "summary": "Good attempt.",
            "strengths": ["Correct scene description"],
            "issues": ["Missing detail about ducks"],
            "suggestions": ["Add more detail about the animals"],
        }
        semantic_plan = {"difficulty_level": "beginner", "scene": "park"}
        standard_answer = "A child feeds ducks in the park."
        user_text = "A kid in the park."

        with patch.object(QwenClient, "_chat", return_value=json.dumps(evaluation)):
            client = QwenClient()
            result = client.evaluate_practice(semantic_plan, standard_answer, user_text)

        assert result == evaluation
        assert result["relevance_score"] == 85
        assert result["fluency_score"] == 72

    def test_evaluate_practice_invalid_json(self):
        """RuntimeError when _chat returns non-JSON text."""
        semantic_plan = {"difficulty_level": "beginner", "scene": "park"}

        with patch.object(QwenClient, "_chat", return_value="<html>error page</html>"):
            client = QwenClient()
            with pytest.raises(RuntimeError, match="Failed to parse practice evaluation JSON"):
                client.evaluate_practice(semantic_plan, "answer", "user text")
