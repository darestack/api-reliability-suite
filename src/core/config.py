from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
  # API Settings
  PROJECT_NAME: str = "API Reliability Suite"
  DEBUG: bool = False

  # Observability Settings
  LOG_LEVEL: str = "info"
  OTLP_ENDPOINT: str | None = None # Where to send the traces

  # Security Settings
  SECRET_KEY: str = "change-me-in-production"

  ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

  model_config = SettingsConfigDict(
    env_file=".env"
  )

settings = Settings()
