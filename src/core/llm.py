"""
Multi-Provider LLM Adapter
Automatically uses whichever provider has an API key configured.
Priority: Groq > OpenAI > Google
"""

import json
import re
from typing import Any

from src.core.config import settings
import structlog

logger = structlog.get_logger()


async def summarize_with_llm(logs: list[str]) -> dict[str, Any]:
    """
    Sends logs to an LLM and returns a structured summary.
    Returns a dict with 'summary_text' and 'structured_insight'.
    """
    if not logs:
        return {
            "summary_text": "No recent logs to analyze.",
            "structured_insight": None,
        }

    # Prepare variables for the prompt
    recent_logs = logs[-20:]
    formatted_logs = chr(10).join(recent_logs)

    prompt = f"""
You are a senior API reliability engineer assisting with incident triage.

Analyze the following recent API error logs and extract actionable insights.

Recent Error Logs ({len(recent_logs)} entries, most recent last):
{formatted_logs}

### Requirements:
Please provide your analysis in a structured format:
1. **Executive Summary**: 2-3 sentence overview.
2. **Patterns Identified**: Recurring issues.
3. **Remediation Steps**: Bulleted immediate actions.
4. **Structured JSON**: Include a block at the very end using this schema:
   ```json
   {{
     "root_cause_id": "brief_id",
     "severity": "CRITICAL|HIGH|MEDIUM|LOW",
     "action": ["step1", "step2"]
   }}
   ```
"""
    # Get raw response
    raw_text = "No LLM configured."
    if settings.GROQ_API_KEY:
        raw_text = await _call_groq(prompt)
    elif settings.OPENAI_API_KEY:
        raw_text = await _call_openai(prompt)
    elif settings.GOOGLE_API_KEY:
        raw_text = await _call_google(prompt)
    else:
        return {
            "summary_text": "No LLM configured. Set GROQ/OPENAI_API_KEY.",
            "structured_insight": None,
        }

    # Parse JSON block
    structured_data = None
    summary_text = raw_text

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

    return {"summary_text": summary_text, "structured_insight": structured_data}


async def _call_groq(prompt: str) -> str:
    from groq import AsyncGroq

    client = AsyncGroq(api_key=settings.GROQ_API_KEY)
    try:
        response = await client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=500,
        )
        return response.choices[0].message.content
    except Exception as e:
        logger.error("groq_api_error", error=str(e))
        return f"Groq Error: {str(e)}"


async def _call_openai(prompt: str) -> str:
    from openai import AsyncOpenAI

    client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)
    try:
        response = await client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=500,
        )
        return response.choices[0].message.content
    except Exception as e:
        logger.error("openai_api_error", error=str(e))
        return f"OpenAI Error: {str(e)}"


async def _call_google(prompt: str) -> str:
    import google.generativeai as genai

    # Note: generativeai's generate_content is blocking, but we can wrap it if needed.
    # Currently, there isn't a native 'AsyncGenerativeModel' in the standard SDK
    # that is as widely used as AsyncOpenAI, but we can use thread pools or simply
    # await if the SDK supports it. Actually, some versions support async.
    try:
        genai.configure(api_key=settings.GOOGLE_API_KEY)
        model = genai.GenerativeModel("gemini-1.5-flash")
        response = await model.generate_content_async(prompt)
        return response.text
    except Exception as e:
        logger.error("google_api_error", error=str(e))
        return f"Google Error: {str(e)}"
