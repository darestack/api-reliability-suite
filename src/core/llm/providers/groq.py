from src.core.llm.providers.base import BaseLLM
import structlog

logger = structlog.get_logger()


class GroqProvider(BaseLLM):
    """Groq provider implementation."""

    def __init__(self, api_key: str):
        self.api_key = api_key
        try:
            from groq import AsyncGroq

            self.client = AsyncGroq(api_key=self.api_key)
        except ImportError:
            logger.error("groq_not_installed")
            raise ImportError("Please install 'groq' package.")

    async def generate(self, prompt: str) -> str:
        try:
            response = await self.client.chat.completions.create(
                model="llama-3.1-8b-instant",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=1000,
            )
            return response.choices[0].message.content
        except Exception as e:
            logger.error("groq_api_error", error=str(e))
            return f"Groq Error: {str(e)}"
