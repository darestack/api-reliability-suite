from src.core.config import settings
from src.core.llm.providers.base import BaseLLM
from src.core.llm.providers.openai import OpenAIProvider
from src.core.llm.providers.groq import GroqProvider
from src.core.llm.providers.google import GoogleProvider
import structlog

logger = structlog.get_logger()


class LLMFactory:
    """Factory to create and manage the active LLM provider."""

    @staticmethod
    def get_provider_with_name() -> tuple[str | None, BaseLLM | None]:
        """Return the active provider name and instance using priority Groq > OpenAI > Google."""
        if settings.GROQ_API_KEY:
            logger.info("llm_factory_selection", provider="groq")
            return "groq", GroqProvider(api_key=settings.GROQ_API_KEY)

        if settings.OPENAI_API_KEY:
            logger.info("llm_factory_selection", provider="openai")
            return "openai", OpenAIProvider(api_key=settings.OPENAI_API_KEY)

        if settings.GOOGLE_API_KEY:
            logger.info("llm_factory_selection", provider="google")
            return "google", GoogleProvider(api_key=settings.GOOGLE_API_KEY)

        logger.warning("llm_factory_no_provider_configured")
        return None, None

    @staticmethod
    def get_provider() -> BaseLLM | None:
        """Return only the active provider instance for callers that do not need metadata."""
        _, provider = LLMFactory.get_provider_with_name()
        return provider
