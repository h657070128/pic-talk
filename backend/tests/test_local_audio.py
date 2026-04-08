"""Tests for local_audio utility."""
import sys
from unittest.mock import patch, MagicMock

# Mock sounddevice and scipy before importing
mock_sd = MagicMock()
mock_scipy_write = MagicMock()

sys.modules.setdefault("sounddevice", mock_sd)
if "scipy" not in sys.modules:
    sys.modules["scipy"] = MagicMock()
if "scipy.io" not in sys.modules:
    sys.modules["scipy.io"] = MagicMock()
if "scipy.io.wavfile" not in sys.modules:
    mock_wavfile = MagicMock()
    mock_wavfile.write = mock_scipy_write
    sys.modules["scipy.io.wavfile"] = mock_wavfile


class TestRecordLocalAudio:
    @patch("services.local_audio.write")
    @patch("services.local_audio.sd")
    def test_record_local_audio(self, mock_sd_patched, mock_write):
        mock_audio = MagicMock()
        mock_sd_patched.rec.return_value = mock_audio

        from services.local_audio import record_local_audio

        record_local_audio(seconds=3, filename="output.wav")

        mock_sd_patched.rec.assert_called_once()
        call_args = mock_sd_patched.rec.call_args
        assert call_args[0][0] == 3 * 16000
        assert call_args[1]["samplerate"] == 16000
        assert call_args[1]["channels"] == 1

        mock_sd_patched.wait.assert_called_once()
        mock_write.assert_called_once_with("output.wav", 16000, mock_audio)

    @patch("services.local_audio.write")
    @patch("services.local_audio.sd")
    def test_record_local_audio_defaults(self, mock_sd_patched, mock_write):
        mock_sd_patched.rec.return_value = MagicMock()

        from services.local_audio import record_local_audio

        record_local_audio()

        call_args = mock_sd_patched.rec.call_args
        assert call_args[0][0] == 5 * 16000
        mock_write.assert_called_once()
        assert mock_write.call_args[0][0] == "test_audio.wav"
