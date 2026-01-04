"""
Multi-Provider LLM Adapter
Automatically uses whichever provider has an API key configured.
Priority: Groq > OpenAI > Google
"""

from src.core.config import settings
import structlog

logger = structlog.get_logger()

async def summarize_with_llm(logs: list[str]) -> str:
  """
    Sends logs to an LLM and returns a human-readable summary.
    Auto-selects provider based on available API keys.
  """
  if not logs:
    return "No recent logs to analyze."

  # Prepare variables for the prompt
  recent_logs = logs[-20:] # Analyze last 20 entries
  formatted_logs = chr(10).join(recent_logs) # Join with newlines

  prompt = f"""
You are a senior API reliability engineer assisting with incident triage.

Analyze the following recent API error logs and extract actionable insights.

Recent Error Logs ({len(recent_logs)} entries, most recent last):
{formatted_logs}

Please provide:
1. A concise 2–3 sentence summary of the primary issues
2. Any recurring patterns or correlations (reference log numbers explicitly where relevant)
3. Recommended immediate remediation steps
4. Likely root causes, based strictly on the evidence in the logs

Guidelines:
- Prioritize findings by severity and impact
- Avoid speculation not supported by the logs (Always be factual and realistic.)
- Write clearly for an on-call engineering team responding to an incident
"""
   # Try providers in order of preference
  if settings.GROQ_API_KEY:
    return await _call_groq(prompt)
  elif settings.OPENAI_API_KEY:
    return await _call_openai(prompt)
  elif settings.GOOGLE_API_KEY:
    return await _call_google(prompt)
  else:
    return "No LLM configured. Set GROQ_API_KEY, OPENAI_API_KEY, or GOOGLE_API_KEY"

async def _call_groq(prompt: str) -> str:
  from groq import Groq
  client = Groq(api_key=settings.GROQ_API_KEY)
  response = client.chat.completions.create(
    model="llama-3.1-8b-instant",
    messages=[{"role": "user", "content": prompt}],
    max_tokens=300
  )
  return response.choices[0].message.content

async def _call_openai(prompt: str) -> str:
  from openai import OpenAI
  client = OpenAI(api_key=settings.OPENAI_API_KEY)
  response = client.chat.completions.create(
    model="gpt-4o-mini",
    messages=[{"role": "user", "content": prompt}],
    max_tokens=300
  )
  return response.choices[0].message.content

async def _call_google(prompt: str) -> str:
  import google.generativeai as genai
  genai.configure(api_key=settings.GOOGLE_API_KEY)
  model = genai.GenerativeModel("gemini-1.5-flash")
  response = model.generate_content(prompt)
  return response.text