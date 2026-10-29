import pytest
from backend.app.core.config import validate_auth_secret, DEFAULT_DEV_SECRET

STRONG = "x" * 40


def test_dev_allows_default():
    validate_auth_secret(DEFAULT_DEV_SECRET, "development", False)


def test_production_rejects_default():
    with pytest.raises(RuntimeError):
        validate_auth_secret(DEFAULT_DEV_SECRET, "production", False)


def test_production_rejects_short():
    with pytest.raises(RuntimeError):
        validate_auth_secret("short", "production", False)


def test_render_rejects_missing():
    with pytest.raises(RuntimeError):
        validate_auth_secret("", "development", True)


def test_production_accepts_strong():
    validate_auth_secret(STRONG, "production", True)