import pytest
from unittest.mock import AsyncMock, patch, MagicMock
from src.core.config import settings
from src.core.llm.providers.groq import GROQ_MODEL
from src.core.llm.providers.groq import GroqProvider


class TestGroqProvider:
    @patch("groq.AsyncGroq")
    async def test_generate_success(self, mock_groq):
        # Setup mock client
        mock_client = AsyncMock()
        mock_groq.return_value = mock_client
        mock_client.chat.completions.create.return_value = MagicMock(
            choices=[MagicMock(message=MagicMock(content="Groq response"))]
        )

        provider = GroqProvider(api_key="test-key")
        result = await provider.generate("Test prompt")

        assert result == "Groq response"
        mock_groq.assert_called_once_with(
            api_key="test-key",
            timeout=settings.LLM_REQUEST_TIMEOUT_SECONDS,
            max_retries=settings.LLM_MAX_RETRIES,
        )
        mock_client.chat.completions.create.assert_called_once()

    @patch("groq.AsyncGroq")
    async def test_generate_failure(self, mock_groq):
        # Setup mock client to raise Exception
        mock_client = AsyncMock()
        mock_groq.return_value = mock_client
        mock_client.chat.completions.create.side_effect = Exception("Network Error")

        provider = GroqProvider(api_key="test-key")
        result = await provider.generate("Test prompt")

        assert "Groq Error: Network Error" in result

    def test_init_import_error(self):
        with patch.dict("sys.modules", {"groq": None}):
            with pytest.raises(ImportError) as exc:
                GroqProvider(api_key="test-key")
            assert "Please install 'groq' package" in str(exc.value)

    @patch("groq.AsyncGroq")
    async def test_healthcheck_success(self, mock_groq):
        mock_client = AsyncMock()
        mock_groq.return_value = mock_client
        mock_client.models.retrieve.return_value = MagicMock()

        provider = GroqProvider(api_key="test-key")

        assert await provider.healthcheck() is True
        mock_client.models.retrieve.assert_called_once_with(
            GROQ_MODEL, timeout=settings.LLM_HEALTHCHECK_TIMEOUT_SECONDS
        )
