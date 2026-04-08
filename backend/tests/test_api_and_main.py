"""Tests for API controllers and main app."""
from unittest.mock import patch, MagicMock
from fastapi.testclient import TestClient


class TestHealthCheck:
    def test_health_check(self):
        from main import app
        client = TestClient(app)
        response = client.get("/")
        assert response.status_code == 200
        assert response.json() == {"status": "ok"}


class TestCORSMiddleware:
    def test_cors_allows_localhost(self):
        from main import app
        client = TestClient(app)
        response = client.options(
            "/",
            headers={
                "Origin": "http://localhost:3000",
                "Access-Control-Request-Method": "GET",
            },
        )
        assert response.headers.get("access-control-allow-origin") == "http://localhost:3000"

    def test_cors_blocks_unknown_origin(self):
        from main import app
        client = TestClient(app)
        response = client.options(
            "/",
            headers={
                "Origin": "http://evil.example.com",
                "Access-Control-Request-Method": "GET",
            },
        )
        # CORS should not include the evil origin in allow-origin
        assert response.headers.get("access-control-allow-origin") != "http://evil.example.com"


class TestImageController:
    @patch("api.image_controller.ImageTaskService")
    def test_generate_image_task(self, mock_service_cls):
        mock_service = mock_service_cls.return_value
        mock_service.generate_image_task.return_value = {
            "semantic_plan": {"scene": "park"},
            "image_url": "https://oss.example.com/img.png",
            "standard_answer": {"key_facts": ["child plays"]},
        }

        from main import app
        client = TestClient(app)
        response = client.get("/api/image/generate")

        assert response.status_code == 200
        data = response.json()
        assert "semantic_plan" in data
        assert "image_url" in data
        assert "standard_answer" in data
        mock_service.generate_image_task.assert_called_once_with("beginner")

    @patch("api.image_controller.ImageTaskService")
    def test_get_random_task(self, mock_service_cls):
        mock_service = mock_service_cls.return_value
        mock_service.get_random_task.return_value = {
            "id": 1,
            "image_url": "https://oss.example.com/img.png",
            "difficulty": "beginner",
            "semantic_plan": {"scene": "park"},
            "standard_answer": "A child plays.",
        }

        from main import app
        client = TestClient(app)
        response = client.get("/api/image/get_random_task")

        assert response.status_code == 200
        data = response.json()
        assert data["id"] == 1
        assert "image_url" in data
        mock_service.get_random_task.assert_called_once()

    @patch("api.image_controller.ImageTaskService")
    def test_get_random_task_returns_null_when_empty(self, mock_service_cls):
        mock_service = mock_service_cls.return_value
        mock_service.get_random_task.return_value = None

        from main import app
        client = TestClient(app)
        response = client.get("/api/image/get_random_task")

        assert response.status_code == 200
        assert response.json() is None


class TestUserPracticeController:
    @patch("api.user_practice_controller.PracticeService")
    @patch("api.user_practice_controller.ImageTaskService")
    def test_evaluate_practice_task_not_found(self, mock_img_service_cls, mock_practice_cls):
        mock_img_service = mock_img_service_cls.return_value
        mock_img_service.get_task_by_id.return_value = None

        from main import app
        client = TestClient(app)

        response = client.post(
            "/api/user-practice/evaluate",
            data={"task_id": "999"},
            files={"audio_file": ("test.wav", b"fake audio", "audio/wav")},
        )

        assert response.status_code == 404
        assert "not found" in response.json()["detail"].lower()

    @patch("api.user_practice_controller.PracticeService")
    @patch("api.user_practice_controller.ImageTaskService")
    def test_evaluate_practice_success(self, mock_img_service_cls, mock_practice_cls):
        mock_img_service = mock_img_service_cls.return_value
        mock_practice = mock_practice_cls.return_value

        task = {
            "id": 1,
            "semantic_plan": {"scene": "park"},
            "standard_answer": "A child plays.",
            "image_url": "http://img.url",
        }
        mock_img_service.get_task_by_id.return_value = task
        mock_practice.submit_practice.return_value = {
            "id": 10,
            "asr_text": "child playing",
            "relevance_score": 85,
            "fluency_score": 70,
            "ai_feedback": {"summary": "Good"},
        }

        from main import app
        client = TestClient(app)

        response = client.post(
            "/api/user-practice/evaluate",
            data={"task_id": "1"},
            files={"audio_file": ("test.wav", b"fake audio", "audio/wav")},
        )

        assert response.status_code == 200
        data = response.json()
        assert data["asr_text"] == "child playing"
        assert data["relevance_score"] == 85
        mock_img_service.get_task_by_id.assert_called_once_with(1)

    @patch("api.user_practice_controller.PracticeService")
    @patch("api.user_practice_controller.ImageTaskService")
    def test_evaluate_practice_missing_form_fields(self, mock_img_service_cls, mock_practice_cls):
        from main import app
        client = TestClient(app)

        # Missing task_id
        response = client.post(
            "/api/user-practice/evaluate",
            files={"audio_file": ("test.wav", b"fake audio", "audio/wav")},
        )
        assert response.status_code == 422  # Validation error


class TestRouterRegistration:
    def test_image_routes_registered(self):
        from main import app
        routes = [r.path for r in app.routes]
        assert "/api/image/generate" in routes
        assert "/api/image/get_random_task" in routes

    def test_user_practice_routes_registered(self):
        from main import app
        routes = [r.path for r in app.routes]
        assert "/api/user-practice/evaluate" in routes
