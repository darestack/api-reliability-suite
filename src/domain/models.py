from pydantic import BaseModel, ConfigDict, Field


class CommonBaseModel(BaseModel):
    """Base model with shared configuration for all domain models."""

    model_config = ConfigDict(strict=True, populate_by_name=True)


class HealthStatus(CommonBaseModel):
    """Represents the system health status."""

    status: str = Field(..., description="Overall health status (e.g., 'ok')")
    service: str = Field(..., description="Name of the service reporting status")


class Token(CommonBaseModel):
    """Schema for JWT access tokens."""

    access_token: str = Field(..., description="The JWT access token string")
    token_type: str = Field("bearer", description="The type of token")


class User(CommonBaseModel):
    """Internal user model for authentication."""

    username: str = Field(..., min_length=3, max_length=50)
    hashed_password: str = Field(..., description="Bcrypt hashed password")


class AIRecommendation(CommonBaseModel):
    """Structured insight returned by the LLM analysis agent."""

    root_cause_id: str = Field(
        ..., description="Short identifier for the identified issue"
    )
    severity: str = Field(..., pattern="^(CRITICAL|HIGH|MEDIUM|LOW)$")
    action: list[str] = Field(..., description="List of recommended remediation steps")
