import json


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
