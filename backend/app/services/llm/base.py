"""Abstract base class for LLM providers."""

from abc import ABC, abstractmethod

from pydantic import BaseModel


class SOAPNoteOutput(BaseModel):
    """Structured SOAP note output from LLM extraction.

    Attributes:
        subjective: Patient's reported symptoms, history, complaints
        objective: Observable findings, measurements, examination results
        assessment: Clinical reasoning, diagnosis, contributing factors
        plan: Treatment provided, home program, follow-up plan
    """

    subjective: str
    objective: str
    assessment: str
    plan: str


class BaseLLMClient(ABC):
    """Abstract interface for LLM providers.

    Implementations must provide SOAP note extraction from transcripts.
    This abstraction allows switching between providers (Mistral, Azure OpenAI)
    via configuration only.
    """

    @abstractmethod
    async def extract_soap_note(
        self,
        transcript: str,
        template: str,
        language: str,
    ) -> SOAPNoteOutput:
        """Extract a structured SOAP note from a consultation transcript.

        Args:
            transcript: Transcribed text from the consultation
            template: SOAP template defining expected structure
            language: Output language for the note (fr/de/en)

        Returns:
            SOAPNoteOutput with the 4 SOAP sections
        """
        ...
