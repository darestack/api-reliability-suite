from abc import ABC, abstractmethod


class BaseLLM(ABC):
    """Base interface for all LLM providers."""

    @abstractmethod
    async def generate(self, prompt: str) -> str:
        """Generate a response for the given prompt."""
