"""Tests for services.practice_record_repository.PracticeRecordRepository."""

from unittest.mock import patch, MagicMock

from services.practice_record_repository import PracticeRecordRepository


@patch("services.practice_record_repository.SessionLocal")
def test_save_record(mock_session_local):
    """save_record should add, commit, refresh, and return the record."""
    mock_db = MagicMock()
    mock_session_local.return_value = mock_db

    repo = PracticeRecordRepository()
    result = repo.save_record(
        task_id=1,
        asr_text="I see a dog in the park.",
        ai_feedback={"score": 85, "comment": "Good job"},
        relevance_score=90,
        fluency_score=80,
    )

    mock_db.add.assert_called_once()
    mock_db.commit.assert_called_once()
    mock_db.refresh.assert_called_once()
    added_record = mock_db.add.call_args[0][0]
    assert added_record.task_id == 1
    assert added_record.asr_text == "I see a dog in the park."
    assert added_record.relevance_score == 90
    assert added_record.fluency_score == 80
    assert added_record.user_id is None
    assert added_record.user_audio_url is None


@patch("services.practice_record_repository.SessionLocal")
def test_save_record_with_optional_fields(mock_session_local):
    """save_record should pass user_id and user_audio_url when provided."""
    mock_db = MagicMock()
    mock_session_local.return_value = mock_db

    repo = PracticeRecordRepository()
    repo.save_record(
        task_id=2,
        asr_text="There is a cat.",
        ai_feedback={"score": 70},
        relevance_score=75,
        fluency_score=65,
        user_id=42,
        user_audio_url="https://cdn.example.com/audio/rec.wav",
    )

    added_record = mock_db.add.call_args[0][0]
    assert added_record.user_id == 42
    assert added_record.user_audio_url == "https://cdn.example.com/audio/rec.wav"


@patch("services.practice_record_repository.SessionLocal")
def test_save_record_calls_close(mock_session_local):
    """db.close() must always be called after save_record."""
    mock_db = MagicMock()
    mock_session_local.return_value = mock_db

    repo = PracticeRecordRepository()
    repo.save_record(
        task_id=3,
        asr_text="Hello",
        ai_feedback={},
        relevance_score=50,
        fluency_score=50,
    )

    mock_db.close.assert_called_once()
