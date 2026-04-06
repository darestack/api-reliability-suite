import pytest
from types import SimpleNamespace
from unittest.mock import AsyncMock, MagicMock, patch

from src.core.llm.providers.google import (
    GOOGLE_API_VERSION,
    GOOGLE_MODEL,
    GoogleProvider,
)


class TestGoogleProvider:
    @patch("src.core.llm.providers.google.load_google_genai")
    async def test_generate_success(self, mock_load_google_genai):
        # Setup mock async client
        http_options = SimpleNamespace(api_version=GOOGLE_API_VERSION)
        mock_session = MagicMock()
        mock_session.models.generate_content = AsyncMock(
            return_value=MagicMock(text="Google response")
        )
        mock_aio_client = AsyncMock()
        mock_aio_client.__aenter__.return_value = mock_session
        mock_client = MagicMock(aio=mock_aio_client)
        mock_genai = SimpleNamespace(
            types=SimpleNamespace(
                HttpOptions=MagicMock(return_value=http_options),
            ),
            Client=MagicMock(return_value=mock_client),
        )
        mock_load_google_genai.return_value = mock_genai

        provider = GoogleProvider(api_key="test-key")
        result = await provider.generate("Test prompt")

        assert result == "Google response"
        mock_genai.types.HttpOptions.assert_called_once_with(
            api_version=GOOGLE_API_VERSION
        )
        mock_genai.Client.assert_called_once_with(
            api_key="test-key",
            http_options=http_options,
        )
        mock_session.models.generate_content.assert_called_once_with(
            model=GOOGLE_MODEL,
            contents="Test prompt",
        )

    @patch("src.core.llm.providers.google.load_google_genai")
    async def test_generate_failure(self, mock_load_google_genai):
        # Setup mock async client to raise Exception
        http_options = SimpleNamespace(api_version=GOOGLE_API_VERSION)
        mock_session = MagicMock()
        mock_session.models.generate_content = AsyncMock(
            side_effect=Exception("Quota Exceeded")
        )
        mock_aio_client = AsyncMock()
        mock_aio_client.__aenter__.return_value = mock_session
        mock_client = MagicMock(aio=mock_aio_client)
        mock_genai = SimpleNamespace(
            types=SimpleNamespace(
                HttpOptions=MagicMock(return_value=http_options),
            ),
            Client=MagicMock(return_value=mock_client),
        )
        mock_load_google_genai.return_value = mock_genai

        provider = GoogleProvider(api_key="test-key")
        result = await provider.generate("Test prompt")

        assert "Google Error: Quota Exceeded" in result

    def test_init_import_error(self):
        with patch(
            "src.core.llm.providers.google.load_google_genai",
            side_effect=ImportError("Please install 'google-genai' package."),
        ):
            with pytest.raises(ImportError) as exc:
                GoogleProvider(api_key="test-key")
            assert "Please install 'google-genai' package" in str(exc.value)
