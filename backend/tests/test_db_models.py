"""Tests for SQLAlchemy database models (no live DB required)."""

import pytest
from sqlalchemy import inspect, BigInteger, String, Text, DateTime, JSON, Integer
from db.image_practice_task import ImagePracticeTask
from db.user_practice_record import UserPracticeRecord


# ---------------------------------------------------------------------------
# ImagePracticeTask
# ---------------------------------------------------------------------------
class TestImagePracticeTaskModel:
    """Tests for the ImagePracticeTask ORM model."""

    def test_table_name(self):
        assert ImagePracticeTask.__tablename__ == "image_practice_task"

    def test_expected_columns_exist(self):
        mapper = inspect(ImagePracticeTask)
        column_names = {col.key for col in mapper.columns}
        expected = {
            "id",
            "semantic_plan",
            "image_url",
            "standard_answer",
            "difficulty",
            "created_at",
        }
        assert expected.issubset(column_names)

    def test_primary_key_is_id(self):
        mapper = inspect(ImagePracticeTask)
        pk_cols = [col.name for col in mapper.columns if col.primary_key]
        assert pk_cols == ["id"]

    def test_id_type_is_biginteger(self):
        col = ImagePracticeTask.__table__.columns["id"]
        assert isinstance(col.type, BigInteger)

    def test_semantic_plan_is_json_not_nullable(self):
        col = ImagePracticeTask.__table__.columns["semantic_plan"]
        assert isinstance(col.type, JSON)
        assert col.nullable is False

    def test_image_url_is_string_not_nullable(self):
        col = ImagePracticeTask.__table__.columns["image_url"]
        assert isinstance(col.type, String)
        assert col.nullable is False

    def test_standard_answer_is_text_not_nullable(self):
        col = ImagePracticeTask.__table__.columns["standard_answer"]
        assert isinstance(col.type, Text)
        assert col.nullable is False

    def test_difficulty_is_string_not_nullable(self):
        col = ImagePracticeTask.__table__.columns["difficulty"]
        assert isinstance(col.type, String)
        assert col.nullable is False

    def test_created_at_has_server_default(self):
        col = ImagePracticeTask.__table__.columns["created_at"]
        assert isinstance(col.type, DateTime)
        assert col.server_default is not None


# ---------------------------------------------------------------------------
# UserPracticeRecord
# ---------------------------------------------------------------------------
class TestUserPracticeRecordModel:
    """Tests for the UserPracticeRecord ORM model."""

    def test_table_name(self):
        assert UserPracticeRecord.__tablename__ == "user_practice_record"

    def test_expected_columns_exist(self):
        mapper = inspect(UserPracticeRecord)
        column_names = {col.key for col in mapper.columns}
        expected = {
            "id",
            "task_id",
            "user_id",
            "user_audio_url",
            "asr_text",
            "ai_feedback",
            "relevance_score",
            "fluency_score",
            "created_at",
        }
        assert expected.issubset(column_names)

    def test_primary_key_is_id(self):
        mapper = inspect(UserPracticeRecord)
        pk_cols = [col.name for col in mapper.columns if col.primary_key]
        assert pk_cols == ["id"]

    def test_id_type_is_biginteger(self):
        col = UserPracticeRecord.__table__.columns["id"]
        assert isinstance(col.type, BigInteger)

    # -- nullable flags ------------------------------------------------------
    def test_task_id_not_nullable(self):
        col = UserPracticeRecord.__table__.columns["task_id"]
        assert col.nullable is False

    def test_user_id_nullable(self):
        col = UserPracticeRecord.__table__.columns["user_id"]
        assert col.nullable is True

    def test_user_audio_url_nullable(self):
        col = UserPracticeRecord.__table__.columns["user_audio_url"]
        assert col.nullable is True

    def test_asr_text_not_nullable(self):
        col = UserPracticeRecord.__table__.columns["asr_text"]
        assert col.nullable is False

    def test_ai_feedback_not_nullable(self):
        col = UserPracticeRecord.__table__.columns["ai_feedback"]
        assert col.nullable is False

    def test_relevance_score_nullable(self):
        col = UserPracticeRecord.__table__.columns["relevance_score"]
        assert col.nullable is True

    def test_fluency_score_nullable(self):
        col = UserPracticeRecord.__table__.columns["fluency_score"]
        assert col.nullable is True

    # -- foreign key ---------------------------------------------------------
    def test_task_id_foreign_key(self):
        col = UserPracticeRecord.__table__.columns["task_id"]
        fk_targets = {fk.target_fullname for fk in col.foreign_keys}
        assert "image_practice_task.id" in fk_targets

    # -- relationship --------------------------------------------------------
    def test_task_relationship_exists(self):
        mapper = inspect(UserPracticeRecord)
        relationship_names = {rel.key for rel in mapper.relationships}
        assert "task" in relationship_names

    def test_created_at_has_server_default(self):
        col = UserPracticeRecord.__table__.columns["created_at"]
        assert isinstance(col.type, DateTime)
        assert col.server_default is not None
