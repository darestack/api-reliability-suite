import json
import re
from typing import Any

from src.core.llm.factory import LLMFactory
from src.core.logs import sanitize_log_line_for_llm
import structlog

logger = structlog.get_logger()


async def summarize_with_llm(logs: list[str]) -> dict[str, Any]:
    """
    Analyzes a list of error logs and returns both a human-readable
    summary and structured metadata.
    """
    if not logs:
        return {
            "summary_text": "No recent logs to analyze.",
            "structured_insight": None,
            "provider": None,
        }

    provider_name, provider = LLMFactory.get_provider_with_name()
    if not provider:
        return {
            "summary_text": "No LLM configured. Please set GROQ_API_KEY or OPENAI_API_KEY.",
            "structured_insight": None,
            "provider": None,
        }

    sanitized_logs = [sanitize_log_line_for_llm(log) for log in logs]

    prompt = f"""
    You are a Senior SRE (Site Reliability Engineer).
    Analyze the following sanitized JSON error logs from our application.

    Logs:
    {sanitized_logs}

    1. Provide a concise executive summary of what is happening.
    2. Identify patterns (e.g., specific users, specific endpoints).
    3. Suggest immediate remediation steps.

    Your response MUST include a structured JSON block at the end like this:
    ```json
    {{
      "root_cause_id": "string_identifier",
      "severity": "LOW|MEDIUM|HIGH|CRITICAL",
      "action": ["step1", "step2"]
    }}
    ```
    """

    raw_text = await provider.generate(prompt)

    # Defaults
    summary_text = raw_text
    structured_data = None

    # Extract JSON between ```json and ```
    json_match = re.search(r"```json\s*(\{.*?\})\s*```", raw_text, re.DOTALL)
    if json_match:
        json_str = json_match.group(1)
        try:
            structured_data = json.loads(json_str)
            # Remove the JSON block from the readable text to avoid duplication
            summary_text = raw_text.replace(json_match.group(0), "").strip()
        except json.JSONDecodeError:
            logger.warning("llm_json_parse_error", json_str=json_str)

    return {
        "summary_text": summary_text,
        "structured_insight": structured_data,
        "provider": provider_name,
    }
