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
                HttpRetryOptions=MagicMock(return_value=MagicMock()),
            ),
            Client=MagicMock(return_value=mock_client),
        )
        mock_load_google_genai.return_value = mock_genai

        provider = GoogleProvider(api_key="test-key")
        result = await provider.generate("Test prompt")

        assert result == "Google response"
        assert mock_genai.types.HttpOptions.call_count >= 1
        mock_genai.Client.assert_called_once_with(
            api_key="test-key",
            http_options=provider.http_options,
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
                HttpRetryOptions=MagicMock(return_value=MagicMock()),
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

    @patch("src.core.llm.providers.google.load_google_genai")
    async def test_healthcheck_success(self, mock_load_google_genai):
        http_options = SimpleNamespace(api_version=GOOGLE_API_VERSION)
        health_options = SimpleNamespace(api_version=GOOGLE_API_VERSION)
        mock_session = MagicMock()
        mock_session.models.get = AsyncMock(return_value=MagicMock())
        mock_aio_client = AsyncMock()
        mock_aio_client.__aenter__.return_value = mock_session
        mock_client = MagicMock(aio=mock_aio_client)
        mock_genai = SimpleNamespace(
            types=SimpleNamespace(
                HttpOptions=MagicMock(side_effect=[http_options, health_options]),
                HttpRetryOptions=MagicMock(return_value=MagicMock()),
            ),
            Client=MagicMock(return_value=mock_client),
        )
        mock_load_google_genai.return_value = mock_genai

        provider = GoogleProvider(api_key="test-key")

        assert await provider.healthcheck() is True
        assert mock_genai.Client.call_count == 1
        mock_session.models.get.assert_called_once_with(model=GOOGLE_MODEL)
