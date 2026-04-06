import json
import re
from typing import Any


SENSITIVE_KEYS = {
    "access_token",
    "api_key",
    "apikey",
    "authorization",
    "cookie",
    "email",
    "password",
    "refresh_token",
    "secret",
    "set-cookie",
    "token",
}

EMAIL_PATTERN = re.compile(r"\b[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}\b", re.IGNORECASE)
JWT_PATTERN = re.compile(r"\beyJ[A-Za-z0-9_-]+\.[A-Za-z0-9._-]+\.[A-Za-z0-9._-]+\b")
BEARER_PATTERN = re.compile(r"Bearer\s+[A-Za-z0-9._-]+", re.IGNORECASE)
SECRET_ASSIGNMENT_PATTERN = re.compile(
    r"(?P<key>password|secret|token|api[_-]?key)(?P<sep>\s*[:=]\s*)(?P<value>[^,\s]+)",
    re.IGNORECASE,
)
IPV4_PATTERN = re.compile(r"\b(?:\d{1,3}\.){3}\d{1,3}\b")


def is_error_log_line(line: str) -> bool:
    """Treat structured log lines as errors only when their level or error fields say so."""
    stripped = line.strip()
    if not stripped:
        return False

    try:
        payload = json.loads(stripped)
    except json.JSONDecodeError:
        lowered = stripped.lower()
        return "error" in lowered or "exception" in lowered

    level = str(payload.get("level", "")).lower()
    if level in {"error", "exception", "critical"}:
        return True

    error_value = payload.get("error")
    if error_value:
        return True

    event_text = " ".join(
        str(payload.get(key, ""))
        for key in ("event", "message", "detail")
        if payload.get(key)
    ).lower()
    return "exception" in event_text


def sanitize_log_line_for_llm(line: str) -> str:
    """Redact common secrets and PII before sending logs to an external LLM provider."""
    stripped = line.strip()
    if not stripped:
        return stripped

    try:
        payload = json.loads(stripped)
    except json.JSONDecodeError:
        return _sanitize_text(stripped)

    sanitized_payload = _sanitize_value(payload)
    return json.dumps(sanitized_payload, sort_keys=True)


def _sanitize_value(value: Any) -> Any:
    if isinstance(value, dict):
        sanitized: dict[str, Any] = {}
        for key, item in value.items():
            if key.lower() in SENSITIVE_KEYS:
                sanitized[key] = "[REDACTED]"
            else:
                sanitized[key] = _sanitize_value(item)
        return sanitized
    if isinstance(value, list):
        return [_sanitize_value(item) for item in value]
    if isinstance(value, str):
        return _sanitize_text(value)
    return value


def _sanitize_text(value: str) -> str:
    sanitized = EMAIL_PATTERN.sub("[REDACTED_EMAIL]", value)
    sanitized = JWT_PATTERN.sub("[REDACTED_JWT]", sanitized)
    sanitized = BEARER_PATTERN.sub("Bearer [REDACTED_TOKEN]", sanitized)
    sanitized = SECRET_ASSIGNMENT_PATTERN.sub(
        lambda match: f"{match.group('key')}{match.group('sep')}[REDACTED]",
        sanitized,
    )
    sanitized = IPV4_PATTERN.sub("[REDACTED_IP]", sanitized)
    return sanitized
