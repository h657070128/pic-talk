"""
Shared test fixtures and environment setup.

Loaded by pytest before any test module.  Sets dummy env vars and
stubs third-party packages that are not installed in CI.
"""

import os
import sys
from unittest.mock import MagicMock

# ── 1. Ensure backend/ is on sys.path ──────────────────────────────────────
_backend_dir = os.path.join(os.path.dirname(__file__), os.pardir)
sys.path.insert(0, os.path.abspath(_backend_dir))

# ── 2. Dummy environment variables ─────────────────────────────────────────
_DUMMY_ENV = {
    "DASHSCOPE_API_KEY": "test-dashscope-key",
    "OSS_ACCESS_KEY_ID": "test-oss-id",
    "OSS_ACCESS_KEY_SECRET": "test-oss-secret",
    "OSS_ENDPOINT": "https://oss-test.example.com",
    "OSS_BUCKET_NAME": "test-bucket",
    "OSS_PUBLIC_BASE_URL": "https://cdn.example.com",
    "MYSQL_HOST": "localhost",
    "MYSQL_PORT": "3306",
    "MYSQL_DB": "test_db",
    "MYSQL_USER": "test_user",
    "MYSQL_PASSWORD": "test_password",
}

for key, value in _DUMMY_ENV.items():
    os.environ.setdefault(key, value)

# ── 3. Stub out unavailable third-party packages ───────────────────────────
def _ensure_module_stub(name):
    """Insert a MagicMock into sys.modules if the real package is missing."""
    if name not in sys.modules:
        try:
            __import__(name)
        except (ImportError, OSError):
            sys.modules[name] = MagicMock()

for _pkg in (
    "oss2",
    "dashscope",
    "sounddevice",
    "scipy",
    "scipy.io",
    "scipy.io.wavfile",
):
    _ensure_module_stub(_pkg)
