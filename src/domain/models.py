from pydantic import BaseModel, ConfigDict


class CommonBaseModel(BaseModel):
    model_config = ConfigDict(strict=True)


class HealthStatus(CommonBaseModel):
    status: str
    service: str


class Token(CommonBaseModel):
    access_token: str
    token_type: str


class User(CommonBaseModel):
    username: str
    hashed_password: str


class AIRecommendation(CommonBaseModel):
    root_cause_id: str
    severity: str
    action: str
