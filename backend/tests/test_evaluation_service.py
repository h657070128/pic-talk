"""Tests for EvaluationService."""

import pytest
from services.evaluation_service import EvaluationService


@pytest.fixture
def service():
    """Return a fresh EvaluationService instance."""
    return EvaluationService()


class TestEvaluationServiceEvaluate:
    """Tests for EvaluationService.evaluate()."""

    def test_returns_dict(self, service):
        result = service.evaluate("some text")
        assert isinstance(result, dict)

    def test_has_expected_keys(self, service):
        result = service.evaluate("some text")
        assert "content_match_score" in result
        assert "feedback" in result
        assert "encouragement" in result

    def test_content_match_score_is_80(self, service):
        result = service.evaluate("any input")
        assert result["content_match_score"] == 80

    def test_feedback_is_list(self, service):
        result = service.evaluate("any input")
        assert isinstance(result["feedback"], list)
        assert len(result["feedback"]) > 0

    def test_feedback_entry_has_issue(self, service):
        entry = service.evaluate("text")["feedback"][0]
        assert "issue" in entry
        assert entry["issue"] == "Sentence is too simple"

    def test_feedback_entry_has_suggestion(self, service):
        entry = service.evaluate("text")["feedback"][0]
        assert "suggestion" in entry
        assert entry["suggestion"] == "Try to add more details"

    def test_feedback_entry_has_example(self, service):
        entry = service.evaluate("text")["feedback"][0]
        assert "example" in entry
        assert "kitchen" in entry["example"]

    def test_encouragement_message(self, service):
        result = service.evaluate("anything")
        assert result["encouragement"] == "Good job! Keep practicing."

    def test_different_text_returns_same_mock_result(self, service):
        result_a = service.evaluate("The cat sat on the mat.")
        result_b = service.evaluate("A busy street with many pedestrians.")
        result_c = service.evaluate("")
        assert result_a == result_b == result_c

    def test_empty_string_input(self, service):
        result = service.evaluate("")
        assert result["content_match_score"] == 80
        assert isinstance(result["feedback"], list)

    def test_long_text_input(self, service):
        long_text = "word " * 1000
        result = service.evaluate(long_text)
        assert "content_match_score" in result
        assert "feedback" in result
        assert "encouragement" in result
