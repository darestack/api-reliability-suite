from enum import StrEnum

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


class TokenPair(Token):
    """Access + refresh token pair returned for session-based auth flows."""

    refresh_token: str = Field(..., description="Opaque refresh token")


class UserRole(StrEnum):
    """Application roles used for route-level authorization."""

    ADMIN = "admin"
    USER = "user"


class User(CommonBaseModel):
    """Internal user model for authentication."""

    id: int | None = Field(default=None, description="Persistent user identifier")
    username: str = Field(..., min_length=3, max_length=50)
    hashed_password: str = Field(..., description="Bcrypt hashed password")
    role: UserRole = Field(default=UserRole.USER)
    is_active: bool = Field(default=True)


class AuthenticatedUser(CommonBaseModel):
    """Authenticated principal resolved from JWT + persistence layer."""

    id: int | None = Field(default=None, description="Persistent user identifier")
    username: str = Field(..., min_length=3, max_length=50)
    role: UserRole = Field(..., description="Resolved role for the current user")


class RefreshTokenRequest(CommonBaseModel):
    """Refresh-token rotation request."""

    refresh_token: str = Field(..., min_length=32)


class LogoutRequest(CommonBaseModel):
    """Logout request that can revoke the current refresh token too."""

    refresh_token: str | None = Field(
        default=None,
        description="Optional refresh token to revoke alongside the current access token",
    )


class AIRecommendation(CommonBaseModel):
    """Structured insight returned by the LLM analysis agent."""

    root_cause_id: str = Field(
        ..., description="Short identifier for the identified issue"
    )
    severity: str = Field(..., pattern="^(CRITICAL|HIGH|MEDIUM|LOW)$")
    action: list[str] = Field(..., description="List of recommended remediation steps")
