import pytest
from unittest.mock import AsyncMock, patch, MagicMock
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
