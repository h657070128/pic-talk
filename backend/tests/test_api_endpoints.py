"""Tests for FastAPI API endpoints (main.py, image_controller, user_practice_controller)."""
from unittest.mock import patch, MagicMock

from fastapi.testclient import TestClient

from main import app

client = TestClient(app)


class TestHealthCheck:
    """Tests for the root health-check endpoint."""

    def test_health_check(self):
        """GET / returns 200 and {"status": "ok"}."""
        response = client.get("/")
        assert response.status_code == 200
        assert response.json() == {"status": "ok"}


class TestImageEndpoints:
    """Tests for /api/image/* endpoints."""

    @patch("api.image_controller.ImageTaskService")
    def test_generate_image_task(self, mock_service_cls):
        """GET /api/image/generate returns 200 with mocked result."""
        mock_service = mock_service_cls.return_value
        mock_service.generate_image_task.return_value = {
            "id": 1,
            "image_url": "https://example.com/image.png",
            "semantic_plan": {"scene": "park"},
            "standard_answer": "A child is playing.",
        }

        response = client.get("/api/image/generate")

        assert response.status_code == 200
        data = response.json()
        assert data["id"] == 1
        mock_service.generate_image_task.assert_called_once_with("beginner")

    @patch("api.image_controller.ImageTaskService")
    def test_get_random_task(self, mock_service_cls):
        """GET /api/image/get_random_task returns 200 with a task dict."""
        mock_service = mock_service_cls.return_value
        mock_service.get_random_task.return_value = {
            "id": 42,
            "image_url": "https://example.com/random.png",
            "semantic_plan": {"scene": "beach"},
            "standard_answer": "People are swimming.",
        }

        response = client.get("/api/image/get_random_task")

        assert response.status_code == 200
        data = response.json()
        assert data["id"] == 42
        mock_service.get_random_task.assert_called_once()

    @patch("api.image_controller.ImageTaskService")
    def test_get_random_task_none(self, mock_service_cls):
        """GET /api/image/get_random_task returns 200 with null when no task."""
        mock_service = mock_service_cls.return_value
        mock_service.get_random_task.return_value = None

        response = client.get("/api/image/get_random_task")

        assert response.status_code == 200
        assert response.json() is None


class TestUserPracticeEndpoints:
    """Tests for /api/user-practice/* endpoints."""

    @patch("api.user_practice_controller.PracticeService")
    @patch("api.user_practice_controller.ImageTaskService")
    def test_evaluate_practice_success(self, mock_img_cls, mock_practice_cls):
        """POST /api/user-practice/evaluate returns 200 on success."""
        mock_img_service = mock_img_cls.return_value
        mock_practice_service = mock_practice_cls.return_value

        mock_img_service.get_task_by_id.return_value = {
            "id": 1,
            "semantic_plan": {"scene": "park"},
            "standard_answer": "A child is playing.",
        }
        mock_practice_service.submit_practice.return_value = {
            "id": 10,
            "task_id": 1,
            "asr_text": "the child is playing",
            "relevance_score": 85,
            "fluency_score": 70,
        }

        response = client.post(
            "/api/user-practice/evaluate",
            data={"task_id": 1},
            files={"audio_file": ("recording.wav", b"fake audio bytes", "audio/wav")},
        )

        assert response.status_code == 200
        data = response.json()
        assert data["id"] == 10
        assert data["relevance_score"] == 85
        mock_img_service.get_task_by_id.assert_called_once_with(1)
        mock_practice_service.submit_practice.assert_called_once()

    @patch("api.user_practice_controller.PracticeService")
    @patch("api.user_practice_controller.ImageTaskService")
    def test_evaluate_practice_task_not_found(self, mock_img_cls, mock_practice_cls):
        """POST /api/user-practice/evaluate returns 404 when task not found."""
        mock_img_service = mock_img_cls.return_value
        mock_img_service.get_task_by_id.return_value = None

        response = client.post(
            "/api/user-practice/evaluate",
            data={"task_id": 999},
            files={"audio_file": ("recording.wav", b"fake audio bytes", "audio/wav")},
        )

        assert response.status_code == 404
        assert "not found" in response.json()["detail"].lower()
        mock_practice_cls.return_value.submit_practice.assert_not_called()
