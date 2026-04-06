import asyncio

from src.core.config import settings
from src.core.llm.guardrails import llm_bulkhead
from src.core.llm.providers.base import BaseLLM
import structlog

logger = structlog.get_logger()

GOOGLE_MODEL = "gemini-2.5-flash"
GOOGLE_API_VERSION = "v1"


def load_google_genai():
    """Import the supported Google Gen AI SDK."""
    try:
        from google import genai
    except ImportError:
        logger.error("google_genai_not_installed")
        raise ImportError("Please install 'google-genai' package.")

    return genai


class GoogleProvider(BaseLLM):
    """Google (Gemini) provider implementation."""

    def __init__(self, api_key: str):
        self.api_key = api_key
        self.genai = load_google_genai()
        self.http_options = self.genai.types.HttpOptions(
            api_version=GOOGLE_API_VERSION,
            timeout=int(settings.LLM_REQUEST_TIMEOUT_SECONDS * 1000),
            retry_options=self.genai.types.HttpRetryOptions(
                attempts=settings.LLM_MAX_RETRIES + 1
            ),
        )

    async def generate(self, prompt: str) -> str:
        try:
            client = self.genai.Client(
                api_key=self.api_key, http_options=self.http_options
            )
            async with llm_bulkhead():
                async with client.aio as aclient:
                    response = await asyncio.wait_for(
                        aclient.models.generate_content(
                            model=GOOGLE_MODEL,
                            contents=prompt,
                        ),
                        timeout=settings.LLM_REQUEST_TIMEOUT_SECONDS + 1,
                    )
            return response.text
        except Exception as e:
            logger.error("google_api_error", error=str(e))
            return f"Google Error: {str(e)}"

    async def healthcheck(self) -> bool:
        try:
            client = self.genai.Client(
                api_key=self.api_key,
                http_options=self.genai.types.HttpOptions(
                    api_version=GOOGLE_API_VERSION,
                    timeout=int(settings.LLM_HEALTHCHECK_TIMEOUT_SECONDS * 1000),
                ),
            )
            async with llm_bulkhead():
                async with client.aio as aclient:
                    await asyncio.wait_for(
                        aclient.models.get(model=GOOGLE_MODEL),
                        timeout=settings.LLM_HEALTHCHECK_TIMEOUT_SECONDS + 1,
                    )
            return True
        except Exception as exc:
            logger.warning("google_healthcheck_failed", error=str(exc))
            return False
