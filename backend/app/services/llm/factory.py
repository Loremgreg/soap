"""Factory for creating LLM client instances based on configuration."""

from app.config import get_settings
from app.services.llm.base import BaseLLMClient


def get_llm_client() -> BaseLLMClient:
    """Create and return the configured LLM client instance.

    Uses the LLM_PROVIDER environment variable to determine which
    implementation to instantiate.

    Returns:
        BaseLLMClient implementation (MistralLLMClient or AzureOpenAILLMClient)

    Raises:
        ValueError: If the configured LLM_PROVIDER is not supported
    """
    settings = get_settings()
    provider = settings.llm_provider

    if provider == "mistral":
        from app.services.llm.mistral import MistralLLMClient

        return MistralLLMClient()
    elif provider == "azure_openai":
        from app.services.llm.azure_openai import AzureOpenAILLMClient

        return AzureOpenAILLMClient()
    else:
        raise ValueError(f"Unsupported LLM provider: {provider}")
