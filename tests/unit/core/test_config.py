from pathlib import Path

import pytest

from src.core.config import (
    DEFAULT_RATE_LIMIT_STORAGE_URI,
    DEFAULT_SECRET_KEY,
    Settings,
    resolve_secrets_dir,
)


def test_resolve_secrets_dir_prefers_configured_existing_directory(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
):
    monkeypatch.setenv("SETTINGS_SECRETS_DIR", str(tmp_path))

    assert resolve_secrets_dir() == tmp_path


def test_settings_reads_secret_key_from_secret_file(tmp_path: Path):
    (tmp_path / "SECRET_KEY").write_text("from-secret-file", encoding="utf-8")

    settings = Settings(_env_file=None, _secrets_dir=tmp_path)

    assert settings.SECRET_KEY == "from-secret-file"


def test_settings_require_non_default_secret_in_production():
    with pytest.raises(ValueError, match="SECRET_KEY must be set"):
        Settings(
            _env_file=None,
            ENVIRONMENT="production",
            RATE_LIMIT_STORAGE_URI="redis://redis:6379/0",
        )


def test_settings_require_shared_rate_limit_storage_in_production():
    with pytest.raises(ValueError, match="RATE_LIMIT_STORAGE_URI must point"):
        Settings(
            _env_file=None,
            ENVIRONMENT="production",
            SECRET_KEY="not-the-demo-secret",
        )


def test_development_defaults_remain_template_friendly():
    settings = Settings(_env_file=None)

    assert settings.SECRET_KEY == DEFAULT_SECRET_KEY
    assert settings.RATE_LIMIT_STORAGE_URI == DEFAULT_RATE_LIMIT_STORAGE_URI
