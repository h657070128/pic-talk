"""Tests for Pydantic schemas."""

import pytest
from schemas.image_task import ImageTaskRequest


class TestImageTaskRequest:
    """Tests for the ImageTaskRequest schema."""

    def test_default_difficulty_level(self):
        """Default difficulty_level should be 'beginner'."""
        task = ImageTaskRequest()
        assert task.difficulty_level == "beginner"

    def test_custom_difficulty_level(self):
        """Should accept a custom difficulty_level string."""
        task = ImageTaskRequest(difficulty_level="advanced")
        assert task.difficulty_level == "advanced"

    def test_difficulty_level_intermediate(self):
        """Should accept 'intermediate' as difficulty_level."""
        task = ImageTaskRequest(difficulty_level="intermediate")
        assert task.difficulty_level == "intermediate"

    def test_difficulty_level_empty_string(self):
        """Should accept an empty string (still a valid str)."""
        task = ImageTaskRequest(difficulty_level="")
        assert task.difficulty_level == ""

    def test_model_fields_contain_difficulty_level(self):
        """The model should declare a 'difficulty_level' field."""
        assert "difficulty_level" in ImageTaskRequest.model_fields

    def test_serialization_default(self):
        """model_dump should include the default value."""
        task = ImageTaskRequest()
        data = task.model_dump()
        assert data == {"difficulty_level": "beginner"}

    def test_serialization_custom(self):
        """model_dump should reflect the custom value."""
        task = ImageTaskRequest(difficulty_level="expert")
        data = task.model_dump()
        assert data == {"difficulty_level": "expert"}

    def test_from_dict(self):
        """Should be constructable from a plain dict via model_validate."""
        data = {"difficulty_level": "hard"}
        task = ImageTaskRequest.model_validate(data)
        assert task.difficulty_level == "hard"

    def test_from_empty_dict_uses_default(self):
        """An empty dict should yield the default value."""
        task = ImageTaskRequest.model_validate({})
        assert task.difficulty_level == "beginner"
