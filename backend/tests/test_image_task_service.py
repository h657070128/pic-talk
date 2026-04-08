"""Tests for services.image_task_service.ImageTaskService."""

from unittest.mock import patch, MagicMock

_PATCH_PREFIX = "services.image_task_service"


@patch(f"{_PATCH_PREFIX}.ImageTaskRepository")
@patch(f"{_PATCH_PREFIX}.OSSClient")
@patch(f"{_PATCH_PREFIX}.QwenImageMaxClient")
@patch(f"{_PATCH_PREFIX}.QwenClient")
def test_generate_image_task(MockQwen, MockQwenImageMax, MockOSS, MockRepo):
    """generate_image_task orchestrates plan, image, upload, answer, save."""
    from services.image_task_service import ImageTaskService

    mock_qwen = MockQwen.return_value
    mock_qwen.generate_semantic_plan.return_value = {"scene": "beach"}
    mock_qwen.generate_standard_answer.return_value = {"answer": "A sunny beach"}

    mock_image_max = MockQwenImageMax.return_value
    mock_image_max.generate_image.return_value = "https://tmp.example.com/image.png"

    mock_oss = MockOSS.return_value
    mock_oss.upload_image_from_url.return_value = "https://cdn.example.com/oss/img.png"

    mock_repo_instance = MockRepo.return_value
    mock_repo_instance.save_task.return_value = 99

    service = ImageTaskService()
    result = service.generate_image_task("medium")

    mock_qwen.generate_semantic_plan.assert_called_once_with("medium")
    mock_image_max.generate_image.assert_called_once_with({"scene": "beach"})
    mock_oss.upload_image_from_url.assert_called_once_with("https://tmp.example.com/image.png")
    mock_qwen.generate_standard_answer.assert_called_once_with({"scene": "beach"})
    mock_repo_instance.save_task.assert_called_once_with(
        semantic_plan={"scene": "beach"},
        oss_image_url="https://cdn.example.com/oss/img.png",
        standard_answer={"answer": "A sunny beach"},
        difficulty_level="medium",
    )

    assert result == {
        "semantic_plan": {"scene": "beach"},
        "image_url": "https://cdn.example.com/oss/img.png",
        "standard_answer": {"answer": "A sunny beach"},
    }


@patch(f"{_PATCH_PREFIX}.ImageTaskRepository")
@patch(f"{_PATCH_PREFIX}.OSSClient")
@patch(f"{_PATCH_PREFIX}.QwenImageMaxClient")
@patch(f"{_PATCH_PREFIX}.QwenClient")
def test_get_random_task(MockQwen, MockQwenImageMax, MockOSS, MockRepo):
    """get_random_task delegates to the repository and returns its result."""
    from services.image_task_service import ImageTaskService

    fake_task = {"id": 7, "image_url": "https://cdn.example.com/7.png", "difficulty": "easy"}
    MockRepo.return_value.get_random_task.return_value = fake_task

    service = ImageTaskService()
    result = service.get_random_task()

    assert result == fake_task


@patch(f"{_PATCH_PREFIX}.ImageTaskRepository")
@patch(f"{_PATCH_PREFIX}.OSSClient")
@patch(f"{_PATCH_PREFIX}.QwenImageMaxClient")
@patch(f"{_PATCH_PREFIX}.QwenClient")
def test_get_random_task_none(MockQwen, MockQwenImageMax, MockOSS, MockRepo):
    """get_random_task returns None when no tasks exist."""
    from services.image_task_service import ImageTaskService

    MockRepo.return_value.get_random_task.return_value = None

    service = ImageTaskService()
    result = service.get_random_task()

    assert result is None


@patch(f"{_PATCH_PREFIX}.ImageTaskRepository")
@patch(f"{_PATCH_PREFIX}.OSSClient")
@patch(f"{_PATCH_PREFIX}.QwenImageMaxClient")
@patch(f"{_PATCH_PREFIX}.QwenClient")
def test_get_task_by_id(MockQwen, MockQwenImageMax, MockOSS, MockRepo):
    """get_task_by_id returns the task dict from the repository."""
    from services.image_task_service import ImageTaskService

    fake_task = {"id": 15, "image_url": "https://cdn.example.com/15.png", "difficulty": "hard"}
    MockRepo.return_value.get_task_by_id.return_value = fake_task

    service = ImageTaskService()
    result = service.get_task_by_id(15)

    MockRepo.return_value.get_task_by_id.assert_called_once_with(15)
    assert result == fake_task


@patch(f"{_PATCH_PREFIX}.ImageTaskRepository")
@patch(f"{_PATCH_PREFIX}.OSSClient")
@patch(f"{_PATCH_PREFIX}.QwenImageMaxClient")
@patch(f"{_PATCH_PREFIX}.QwenClient")
def test_get_task_by_id_not_found(MockQwen, MockQwenImageMax, MockOSS, MockRepo):
    """get_task_by_id returns None when the task does not exist."""
    from services.image_task_service import ImageTaskService

    MockRepo.return_value.get_task_by_id.return_value = None

    service = ImageTaskService()
    result = service.get_task_by_id(9999)

    assert result is None
