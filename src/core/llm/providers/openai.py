import asyncio

from src.core.config import settings
from src.core.llm.guardrails import llm_bulkhead
from src.core.llm.providers.base import BaseLLM
import structlog

logger = structlog.get_logger()

OPENAI_MODEL = "gpt-4o-mini"


class OpenAIProvider(BaseLLM):
    """OpenAI provider implementation."""

    def __init__(self, api_key: str):
        self.api_key = api_key
        try:
            from openai import AsyncOpenAI

            self.client = AsyncOpenAI(
                api_key=self.api_key,
                timeout=settings.LLM_REQUEST_TIMEOUT_SECONDS,
                max_retries=settings.LLM_MAX_RETRIES,
            )
        except ImportError:
            logger.error("openai_not_installed")
            raise ImportError("Please install 'openai' package.")

    async def generate(self, prompt: str) -> str:
        try:
            async with llm_bulkhead():
                response = await self.client.chat.completions.create(
                    model=OPENAI_MODEL,
                    messages=[{"role": "user", "content": prompt}],
                    max_tokens=1000,
                )
            return response.choices[0].message.content
        except Exception as e:
            logger.error("openai_api_error", error=str(e))
            return f"OpenAI Error: {str(e)}"

    async def healthcheck(self) -> bool:
        try:
            async with llm_bulkhead():
                await asyncio.wait_for(
                    self.client.models.retrieve(
                        OPENAI_MODEL,
                        timeout=settings.LLM_HEALTHCHECK_TIMEOUT_SECONDS,
                    ),
                    timeout=settings.LLM_HEALTHCHECK_TIMEOUT_SECONDS + 1,
                )
            return True
        except Exception as exc:
            logger.warning("openai_healthcheck_failed", error=str(exc))
            return False
