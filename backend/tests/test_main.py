"""Tests for the FastAPI application entry point and health check."""

from unittest.mock import patch, MagicMock

import pytest
from starlette.testclient import TestClient

from main import app


@pytest.fixture()
def client():
    return TestClient(app)


class TestHealthCheck:
    def test_returns_ok(self, client):
        resp = client.get("/")
        assert resp.status_code == 200
        assert resp.json() == {"status": "ok"}


class TestImageRouterMounted:
    """Verify the image router is reachable (even if the service call is mocked)."""

    def test_generate_endpoint_exists(self, client):
        with patch("api.image_controller.ImageTaskService") as MockSvc:
            MockSvc.return_value.generate_image_task.return_value = {"ok": True}
            resp = client.get("/api/image/generate")
        assert resp.status_code == 200

    def test_get_random_task_endpoint_exists(self, client):
        with patch("api.image_controller.ImageTaskService") as MockSvc:
            MockSvc.return_value.get_random_task.return_value = {"id": 1}
            resp = client.get("/api/image/get_random_task")
        assert resp.status_code == 200


class TestUserPracticeRouterMounted:
    """Verify the user-practice router is reachable."""

    def test_evaluate_requires_form_data(self, client):
        # POST without required form fields should 422
        resp = client.post("/api/user-practice/evaluate")
        assert resp.status_code == 422
