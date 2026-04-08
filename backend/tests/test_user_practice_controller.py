"""Tests for the user practice controller API endpoints."""

import io
from unittest.mock import patch

import pytest
from starlette.testclient import TestClient

from main import app


@pytest.fixture()
def client():
    return TestClient(app)


class TestEvaluatePractice:
    def test_returns_404_when_task_not_found(self, client):
        with patch("api.user_practice_controller.ImageTaskService") as MockImgSvc:
            MockImgSvc.return_value.get_task_by_id.return_value = None

            audio = io.BytesIO(b"fake-audio-data")
            resp = client.post(
                "/api/user-practice/evaluate",
                data={"task_id": "999"},
                files={"audio_file": ("recording.wav", audio, "audio/wav")},
            )

        assert resp.status_code == 404
        assert "not found" in resp.json()["detail"]

    def test_returns_practice_record_on_success(self, client):
        fake_task = {"id": 1, "semantic_plan": {}, "standard_answer": "{}"}
        fake_record = {
            "id": 10,
            "asr_text": "hello world",
            "relevance_score": 85,
            "fluency_score": 90,
            "ai_feedback": {"summary": "good"},
        }

        with patch("api.user_practice_controller.ImageTaskService") as MockImgSvc, \
             patch("api.user_practice_controller.PracticeService") as MockPracSvc:
            MockImgSvc.return_value.get_task_by_id.return_value = fake_task
            MockPracSvc.return_value.submit_practice.return_value = fake_record

            audio = io.BytesIO(b"fake-audio-data")
            resp = client.post(
                "/api/user-practice/evaluate",
                data={"task_id": "1"},
                files={"audio_file": ("recording.wav", audio, "audio/wav")},
            )

        assert resp.status_code == 200
        data = resp.json()
        assert data["asr_text"] == "hello world"
        assert data["relevance_score"] == 85

    def test_422_when_missing_task_id(self, client):
        audio = io.BytesIO(b"data")
        resp = client.post(
            "/api/user-practice/evaluate",
            files={"audio_file": ("recording.wav", audio, "audio/wav")},
        )
        assert resp.status_code == 422

    def test_422_when_missing_audio_file(self, client):
        resp = client.post(
            "/api/user-practice/evaluate",
            data={"task_id": "1"},
        )
        assert resp.status_code == 422
