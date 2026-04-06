import pytest
from unittest.mock import AsyncMock, MagicMock, patch
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
