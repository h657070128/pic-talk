"""Tests for image_controller API endpoints."""
from unittest.mock import patch, MagicMock
from fastapi.testclient import TestClient

with patch("db.database.create_engine") as mock_engine:
    mock_engine.return_value = MagicMock()
    from main import app

client = TestClient(app)
client_no_raise = TestClient(app, raise_server_exceptions=False)


class TestGenerateImageTask:
    @patch("api.image_controller.ImageTaskService")
    def test_generate_returns_200(self, MockService):
        mock_service = MockService.return_value
        mock_service.generate_image_task.return_value = {
            "semantic_plan": {"scene": "park"},
            "image_url": "https://oss.com/img.png",
            "standard_answer": {"key_facts": []},
        }

        response = client.get("/api/image/generate")

        assert response.status_code == 200
        data = response.json()
        assert "semantic_plan" in data
        assert "image_url" in data
        assert "standard_answer" in data

    @patch("api.image_controller.ImageTaskService")
    def test_generate_calls_service_with_beginner(self, MockService):
        mock_service = MockService.return_value
        mock_service.generate_image_task.return_value = {}

        client.get("/api/image/generate")

        mock_service.generate_image_task.assert_called_once_with("beginner")

    @patch("api.image_controller.ImageTaskService")
    def test_generate_service_error(self, MockService):
        mock_service = MockService.return_value
        mock_service.generate_image_task.side_effect = Exception("AI service error")

        response = client_no_raise.get("/api/image/generate")
        assert response.status_code == 500


class TestGetRandomTask:
    @patch("api.image_controller.ImageTaskService")
    def test_get_random_task_returns_200(self, MockService):
        mock_service = MockService.return_value
        mock_service.get_random_task.return_value = {
            "id": 1,
            "semantic_plan": {"scene": "park"},
            "image_url": "https://oss.com/img.png",
            "standard_answer": "{}",
            "difficulty": "beginner",
        }

        response = client.get("/api/image/get_random_task")

        assert response.status_code == 200
        data = response.json()
        assert data["id"] == 1
        assert data["difficulty"] == "beginner"

    @patch("api.image_controller.ImageTaskService")
    def test_get_random_task_returns_null_when_empty(self, MockService):
        mock_service = MockService.return_value
        mock_service.get_random_task.return_value = None

        response = client.get("/api/image/get_random_task")

        assert response.status_code == 200
        assert response.json() is None

    @patch("api.image_controller.ImageTaskService")
    def test_get_random_task_service_error(self, MockService):
        mock_service = MockService.return_value
        mock_service.get_random_task.side_effect = Exception("DB error")

        response = client_no_raise.get("/api/image/get_random_task")
        assert response.status_code == 500
