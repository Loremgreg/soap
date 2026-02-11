"""Azure OpenAI placeholder implementation of the LLM client.

This is a stub for future Azure OpenAI integration. The switch from
Mistral to Azure OpenAI requires only a configuration change
(LLM_PROVIDER=azure_openai) once this implementation is completed.
"""

from app.services.llm.base import BaseLLMClient, SOAPNoteOutput


class AzureOpenAILLMClient(BaseLLMClient):
    """Azure OpenAI stub client for SOAP note extraction.

    This is a placeholder implementation. When Azure OpenAI integration
    is needed, implement the extract_soap_note method using the Azure
    OpenAI SDK.
    """

    async def extract_soap_note(
        self,
        transcript: str,
        template: str,
        language: str,
    ) -> SOAPNoteOutput:
        """Extract a structured SOAP note via Azure OpenAI.

        Args:
            transcript: Transcribed text from the consultation
            template: SOAP template defining expected structure
            language: Output language for the note (fr/de/en)

        Returns:
            SOAPNoteOutput with the 4 SOAP sections

        Raises:
            NotImplementedError: Azure OpenAI integration is not yet available
        """
        raise NotImplementedError(
            "Azure OpenAI LLM client is not yet implemented. "
            "Set LLM_PROVIDER=mistral in your environment configuration."
        )
