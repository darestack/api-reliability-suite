from unittest.mock import MagicMock, patch

from src.core.llm.factory import LLMFactory


class TestLLMFactory:
    """Tests for the LLMFactory provider selection logic."""

    @patch("src.core.llm.factory.GroqProvider")
    @patch("src.core.llm.factory.settings")
    def test_get_provider_groq_priority(self, mock_settings, mock_groq_provider):
        # Setup: Groq is available (highest priority)
        mock_settings.GROQ_API_KEY = "sk-groq-123"
        mock_settings.OPENAI_API_KEY = "sk-openai-123"
        mock_settings.GOOGLE_API_KEY = "sk-google-123"

        expected_provider = MagicMock()
        mock_groq_provider.return_value = expected_provider

        provider = LLMFactory.get_provider()
        assert provider is expected_provider
        mock_groq_provider.assert_called_once_with(api_key="sk-groq-123")

    @patch("src.core.llm.factory.OpenAIProvider")
    @patch("src.core.llm.factory.settings")
    def test_get_provider_openai_fallback(self, mock_settings, mock_openai_provider):
        # Setup: Groq is missing, but OpenAI is available
        mock_settings.GROQ_API_KEY = None
        mock_settings.OPENAI_API_KEY = "sk-openai-123"
        mock_settings.GOOGLE_API_KEY = "sk-google-123"

        expected_provider = MagicMock()
        mock_openai_provider.return_value = expected_provider

        provider = LLMFactory.get_provider()
        assert provider is expected_provider
        mock_openai_provider.assert_called_once_with(api_key="sk-openai-123")

    @patch("src.core.llm.factory.GoogleProvider")
    @patch("src.core.llm.factory.settings")
    def test_get_provider_google_fallback(self, mock_settings, mock_google_provider):
        # Setup: Groq and OpenAI are missing, but Google is available
        mock_settings.GROQ_API_KEY = None
        mock_settings.OPENAI_API_KEY = None
        mock_settings.GOOGLE_API_KEY = "sk-google-123"

        expected_provider = MagicMock()
        mock_google_provider.return_value = expected_provider

        provider = LLMFactory.get_provider()
        assert provider is expected_provider
        mock_google_provider.assert_called_once_with(api_key="sk-google-123")

    @patch("src.core.llm.factory.settings")
    def test_get_provider_none(self, mock_settings):
        # Setup: No providers configured
        mock_settings.GROQ_API_KEY = None
        mock_settings.OPENAI_API_KEY = None
        mock_settings.GOOGLE_API_KEY = None

        provider = LLMFactory.get_provider()
        assert provider is None

    @patch("src.core.llm.factory.OpenAIProvider")
    @patch("src.core.llm.factory.settings")
    def test_get_provider_with_name_returns_runtime_selection(
        self, mock_settings, mock_openai_provider
    ):
        mock_settings.GROQ_API_KEY = None
        mock_settings.OPENAI_API_KEY = "sk-openai-123"
        mock_settings.GOOGLE_API_KEY = None

        expected_provider = MagicMock()
        mock_openai_provider.return_value = expected_provider

        provider_name, provider = LLMFactory.get_provider_with_name()

        assert provider_name == "openai"
        assert provider is expected_provider
