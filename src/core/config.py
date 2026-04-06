import os
from pathlib import Path
from typing import Literal

from pydantic_settings import BaseSettings, SettingsConfigDict


DEFAULT_SECRET_KEY = "change-me-in-production"
DEFAULT_RATE_LIMIT_STORAGE_URI = "memory://"


def resolve_secrets_dir() -> Path | None:
    configured_dir = os.getenv("SETTINGS_SECRETS_DIR") or os.getenv("SECRETS_DIR")
    candidates = [configured_dir, "/run/secrets"]

    for candidate in candidates:
        if not candidate:
            continue
        path = Path(candidate)
        if path.is_dir():
            return path

    return None


class Settings(BaseSettings):
    # API Settings
    PROJECT_NAME: str = "API Reliability Suite"
    ENVIRONMENT: Literal["development", "test", "staging", "production"] = "development"
    DEBUG: bool = False

    # Observability Settings
    LOG_LEVEL: str = "info"
    LOG_FILE_PATH: str = "app.json"
    OTLP_ENDPOINT: str | None = None  # Where to send the traces

    # LLM Provider Keys (set One of these)
    OPENAI_API_KEY: str | None = None
    GROQ_API_KEY: str | None = None
    GOOGLE_API_KEY: str | None = None

    # Security Settings
    SECRET_KEY: str = DEFAULT_SECRET_KEY

    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    # Rate limiting
    RATE_LIMIT_STORAGE_URI: str = DEFAULT_RATE_LIMIT_STORAGE_URI
    RATE_LIMIT_HEADERS_ENABLED: bool = False
    RATE_LIMIT_IN_MEMORY_FALLBACK_ENABLED: bool = False
    RATE_LIMIT_KEY_PREFIX: str = "api-reliability-suite"

    model_config = SettingsConfigDict(env_file=".env", strict=True)

    def model_post_init(self, __context) -> None:
        protected_environment = self.ENVIRONMENT in {"staging", "production"}

        if protected_environment and self.SECRET_KEY == DEFAULT_SECRET_KEY:
            raise ValueError(
                "SECRET_KEY must be set to a non-default value when ENVIRONMENT is staging or production."
            )

        if (
            protected_environment
            and self.RATE_LIMIT_STORAGE_URI == DEFAULT_RATE_LIMIT_STORAGE_URI
        ):
            raise ValueError(
                "RATE_LIMIT_STORAGE_URI must point to shared storage when ENVIRONMENT is staging or production."
            )


def build_settings() -> Settings:
    return Settings(_secrets_dir=resolve_secrets_dir())


settings = build_settings()
