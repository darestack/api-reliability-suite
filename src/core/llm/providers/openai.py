from src.core.llm.providers.base import BaseLLM
import structlog

logger = structlog.get_logger()


class OpenAIProvider(BaseLLM):
    """OpenAI provider implementation."""

    def __init__(self, api_key: str):
        self.api_key = api_key
        try:
            from openai import AsyncOpenAI

            self.client = AsyncOpenAI(api_key=self.api_key)
        except ImportError:
            logger.error("openai_not_installed")
            raise ImportError("Please install 'openai' package.")

    async def generate(self, prompt: str) -> str:
        try:
            response = await self.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=1000,
            )
            return response.choices[0].message.content
        except Exception as e:
            logger.error("openai_api_error", error=str(e))
            return f"OpenAI Error: {str(e)}"
