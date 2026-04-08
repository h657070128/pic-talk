"""Tests for services.image_task_repository.ImageTaskRepository."""

import json
from unittest.mock import patch, MagicMock

from services.image_task_repository import ImageTaskRepository


@patch("services.image_task_repository.SessionLocal")
def test_save_task(mock_session_local):
    """save_task should add, commit, refresh, and return the task id."""
    mock_db = MagicMock()
    mock_session_local.return_value = mock_db

    def _set_id(task):
        task.id = 42

    mock_db.refresh.side_effect = _set_id

    repo = ImageTaskRepository()
    result = repo.save_task(
        semantic_plan={"scene": "park"},
        oss_image_url="https://cdn.example.com/img.png",
        standard_answer={"answer": "A park"},
        difficulty_level="easy",
    )

    assert result == 42
    mock_db.add.assert_called_once()
    mock_db.commit.assert_called_once()
    mock_db.refresh.assert_called_once()


@patch("services.image_task_repository.SessionLocal")
def test_save_task_calls_close(mock_session_local):
    """db.close() must be called even when commit succeeds."""
    mock_db = MagicMock()
    mock_session_local.return_value = mock_db

    def _set_id(task):
        task.id = 1

    mock_db.refresh.side_effect = _set_id

    repo = ImageTaskRepository()
    repo.save_task(
        semantic_plan={},
        oss_image_url="http://x.png",
        standard_answer={},
        difficulty_level="medium",
    )

    mock_db.close.assert_called_once()


@patch("services.image_task_repository.SessionLocal")
def test_get_random_task_found(mock_session_local):
    """get_random_task returns a dict when a row exists."""
    mock_db = MagicMock()
    mock_session_local.return_value = mock_db

    fake_row = {"id": 5, "image_url": "https://cdn.example.com/img.png", "difficulty": "hard"}
    mock_db.execute.return_value.mappings.return_value.first.return_value = fake_row

    repo = ImageTaskRepository()
    result = repo.get_random_task()

    assert result == fake_row
    mock_db.execute.assert_called_once()
    mock_db.close.assert_called_once()


@patch("services.image_task_repository.SessionLocal")
def test_get_random_task_not_found(mock_session_local):
    """get_random_task returns None when no rows exist."""
    mock_db = MagicMock()
    mock_session_local.return_value = mock_db
    mock_db.execute.return_value.mappings.return_value.first.return_value = None

    repo = ImageTaskRepository()
    result = repo.get_random_task()

    assert result is None
    mock_db.close.assert_called_once()


@patch("services.image_task_repository.SessionLocal")
def test_get_task_by_id_found(mock_session_local):
    """get_task_by_id returns a dict when the task exists."""
    mock_db = MagicMock()
    mock_session_local.return_value = mock_db

    fake_row = {"id": 10, "image_url": "https://cdn.example.com/10.png", "difficulty": "easy"}
    mock_db.execute.return_value.mappings.return_value.first.return_value = fake_row

    repo = ImageTaskRepository()
    result = repo.get_task_by_id(10)

    assert result == fake_row
    mock_db.execute.assert_called_once()
    mock_db.close.assert_called_once()


@patch("services.image_task_repository.SessionLocal")
def test_get_task_by_id_not_found(mock_session_local):
    """get_task_by_id returns None when the task does not exist."""
    mock_db = MagicMock()
    mock_session_local.return_value = mock_db
    mock_db.execute.return_value.mappings.return_value.first.return_value = None

    repo = ImageTaskRepository()
    result = repo.get_task_by_id(999)

    assert result is None
    mock_db.close.assert_called_once()
