from unittest.mock import AsyncMock, patch
from src.core.llm.summarizer import summarize_with_llm


class TestSummarizer:
    @patch("src.core.llm.summarizer.LLMFactory")
    async def test_summarize_success(self, mock_factory):
        # Setup mock factory and provider
        mock_provider = AsyncMock()
        mock_factory.get_provider_with_name.return_value = ("groq", mock_provider)

        # Mock LLM response with a JSON block
        mock_provider.generate.return_value = """
Executive Summary: Things are mostly okay, but there was one small hiccup.
Patterns Identified: One-off network timeout.
Remediation Steps: - Retry the request.
```json
{
  "root_cause_id": "network_timeout",
  "severity": "LOW",
  "action": ["retry"]
}
```
"""

        logs = ["2023-01-01 10:00:00 ERROR: Connection timed out"]
        result = await summarize_with_llm(logs)

        assert "Things are mostly okay" in result["summary_text"]
        assert result["structured_insight"]["root_cause_id"] == "network_timeout"
        assert result["structured_insight"]["severity"] == "LOW"
        assert "retry" in result["structured_insight"]["action"]
        assert result["provider"] == "groq"
        mock_provider.generate.assert_called_once()

    @patch("src.core.llm.summarizer.LLMFactory")
    async def test_summarize_no_provider(self, mock_factory):
        mock_factory.get_provider_with_name.return_value = (None, None)

        logs = ["some log"]
        result = await summarize_with_llm(logs)

        assert "No LLM configured" in result["summary_text"]
        assert result["structured_insight"] is None
        assert result["provider"] is None

    async def test_summarize_empty_logs(self):
        result = await summarize_with_llm([])
        assert "No recent logs to analyze" in result["summary_text"]
        assert result["structured_insight"] is None
        assert result["provider"] is None

    @patch("src.core.llm.summarizer.LLMFactory")
    async def test_summarize_malformed_json(self, mock_factory):
        mock_provider = AsyncMock()
        mock_factory.get_provider_with_name.return_value = ("openai", mock_provider)
        mock_provider.generate.return_value = """
Summary info here.
```json
{ "broken": "json"
```
"""
        logs = ["error"]
        result = await summarize_with_llm(logs)

        # Should still return the text, but structured_insight should be None
        assert "Summary info here" in result["summary_text"]
        assert result["structured_insight"] is None
        assert result["provider"] == "openai"
