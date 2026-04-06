import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from src.core.config import settings
from src.core.llm.providers.openai import OPENAI_MODEL
from src.core.llm.providers.openai import OpenAIProvider


class TestOpenAIProvider:
    @patch("openai.AsyncOpenAI")
    async def test_generate_success(self, mock_openai):
        # Setup mock client
        mock_client = AsyncMock()
        mock_openai.return_value = mock_client
        mock_client.chat.completions.create.return_value = MagicMock(
            choices=[MagicMock(message=MagicMock(content="Success response"))]
        )

        provider = OpenAIProvider(api_key="test-key")
        result = await provider.generate("Test prompt")

        assert result == "Success response"
        mock_openai.assert_called_once_with(
            api_key="test-key",
            timeout=settings.LLM_REQUEST_TIMEOUT_SECONDS,
            max_retries=settings.LLM_MAX_RETRIES,
        )
        mock_client.chat.completions.create.assert_called_once()

    @patch("openai.AsyncOpenAI")
    async def test_generate_failure(self, mock_openai):
        # Setup mock client to raise Exception
        mock_client = AsyncMock()
        mock_openai.return_value = mock_client
        mock_client.chat.completions.create.side_effect = Exception("API Error")

        provider = OpenAIProvider(api_key="test-key")
        result = await provider.generate("Test prompt")

        assert "OpenAI Error: API Error" in result

    def test_init_import_error(self):
        with patch.dict("sys.modules", {"openai": None}):
            with pytest.raises(ImportError) as exc:
                OpenAIProvider(api_key="test-key")
            assert "Please install 'openai' package" in str(exc.value)

    @patch("openai.AsyncOpenAI")
    async def test_healthcheck_success(self, mock_openai):
        mock_client = AsyncMock()
        mock_openai.return_value = mock_client
        mock_client.models.retrieve.return_value = MagicMock()

        provider = OpenAIProvider(api_key="test-key")

        assert await provider.healthcheck() is True
        mock_client.models.retrieve.assert_called_once_with(
            OPENAI_MODEL, timeout=settings.LLM_HEALTHCHECK_TIMEOUT_SECONDS
        )
