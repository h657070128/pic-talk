"""Tests for services.oss_client.OSSClient."""

import os
from unittest.mock import patch, MagicMock

import pytest


@patch("services.oss_client.oss2.Bucket")
@patch("services.oss_client.oss2.Auth")
def test_init(MockAuth, MockBucket):
    """OSSClient.__init__ creates Auth and Bucket from env vars."""
    from services.oss_client import OSSClient

    mock_auth_instance = MockAuth.return_value

    client = OSSClient()

    MockAuth.assert_called_once_with(
        os.getenv("OSS_ACCESS_KEY_ID"),
        os.getenv("OSS_ACCESS_KEY_SECRET"),
    )
    MockBucket.assert_called_once_with(
        mock_auth_instance,
        os.getenv("OSS_ENDPOINT"),
        os.getenv("OSS_BUCKET_NAME"),
    )
    assert client.public_base_url == os.getenv("OSS_PUBLIC_BASE_URL")


@patch("services.oss_client.uuid.uuid4")
@patch("services.oss_client.requests.get")
@patch("services.oss_client.oss2.Bucket")
@patch("services.oss_client.oss2.Auth")
def test_upload_image_from_url(MockAuth, MockBucket, mock_requests_get, mock_uuid4):
    """upload_image_from_url downloads, uploads to OSS, returns public URL."""
    from services.oss_client import OSSClient

    mock_response = MagicMock()
    mock_response.content = b"\x89PNG fake image data"
    mock_requests_get.return_value = mock_response

    mock_uuid4.return_value = MagicMock(hex="abc123def456")

    mock_bucket_instance = MockBucket.return_value

    client = OSSClient()
    result = client.upload_image_from_url("https://tmp.example.com/img.png")

    mock_requests_get.assert_called_once_with("https://tmp.example.com/img.png")
    mock_response.raise_for_status.assert_called_once()
    mock_bucket_instance.put_object.assert_called_once_with(
        "generated-images/abc123def456.png",
        b"\x89PNG fake image data",
    )
    expected_url = f"{os.getenv('OSS_PUBLIC_BASE_URL')}/generated-images/abc123def456.png"
    assert result == expected_url


@patch("services.oss_client.requests.get")
@patch("services.oss_client.oss2.Bucket")
@patch("services.oss_client.oss2.Auth")
def test_upload_image_from_url_http_error(MockAuth, MockBucket, mock_requests_get):
    """upload_image_from_url propagates HTTP errors from requests.get."""
    from services.oss_client import OSSClient
    import requests

    mock_response = MagicMock()
    mock_response.raise_for_status.side_effect = requests.exceptions.HTTPError("404 Not Found")
    mock_requests_get.return_value = mock_response

    client = OSSClient()

    with pytest.raises(requests.exceptions.HTTPError, match="404 Not Found"):
        client.upload_image_from_url("https://bad.example.com/missing.png")


@patch("services.oss_client.oss2.Bucket")
@patch("services.oss_client.oss2.Auth")
def test_upload_bytes(MockAuth, MockBucket):
    """upload_bytes uploads raw bytes and returns the public URL."""
    from services.oss_client import OSSClient

    mock_bucket_instance = MockBucket.return_value

    client = OSSClient()
    result = client.upload_bytes("audio/recording.wav", b"RIFF audio data")

    mock_bucket_instance.put_object.assert_called_once_with(
        "audio/recording.wav",
        b"RIFF audio data",
        headers={},
    )
    expected_url = f"{os.getenv('OSS_PUBLIC_BASE_URL')}/audio/recording.wav"
    assert result == expected_url


@patch("services.oss_client.oss2.Bucket")
@patch("services.oss_client.oss2.Auth")
def test_upload_bytes_with_content_type(MockAuth, MockBucket):
    """upload_bytes passes Content-Type header when provided."""
    from services.oss_client import OSSClient

    mock_bucket_instance = MockBucket.return_value

    client = OSSClient()
    result = client.upload_bytes(
        "audio/recording.wav",
        b"RIFF audio data",
        content_type="audio/wav",
    )

    mock_bucket_instance.put_object.assert_called_once_with(
        "audio/recording.wav",
        b"RIFF audio data",
        headers={"Content-Type": "audio/wav"},
    )
    expected_url = f"{os.getenv('OSS_PUBLIC_BASE_URL')}/audio/recording.wav"
    assert result == expected_url
