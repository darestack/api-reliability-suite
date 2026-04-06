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

    async def generate(self, prompt: str) -> str:
        try:
            client = self.genai.Client(
                api_key=self.api_key,
                http_options=self.genai.types.HttpOptions(
                    api_version=GOOGLE_API_VERSION
                ),
            )
            async with client.aio as aclient:
                response = await aclient.models.generate_content(
                    model=GOOGLE_MODEL,
                    contents=prompt,
                )
            return response.text
        except Exception as e:
            logger.error("google_api_error", error=str(e))
            return f"Google Error: {str(e)}"
