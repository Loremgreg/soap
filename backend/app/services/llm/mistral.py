"""Mistral AI implementation of the LLM client."""

import json
import logging

from mistralai import Mistral

from app.config import get_settings
from app.services.llm.base import BaseLLMClient, SOAPNoteOutput
from app.services.llm.prompts.soap_extraction import (
    build_soap_system_prompt,
    build_soap_user_prompt,
    validate_soap_json_structure,
)

logger = logging.getLogger(__name__)


class MistralLLMClient(BaseLLMClient):
    """Mistral AI client for SOAP note extraction.

    Uses the mistral-large-2 model with JSON output mode for structured
    extraction of SOAP notes from physiotherapy consultation transcripts.
    """

    def __init__(self) -> None:
        """Initialize Mistral client with API key from settings."""
        settings = get_settings()
        self.client = Mistral(api_key=settings.mistral_api_key)
        self.model = "mistral-large-2"

    async def extract_soap_note(
        self,
        transcript: str,
        template: str,
        language: str,
    ) -> SOAPNoteOutput:
        """Extract a structured SOAP note via Mistral AI.

        Args:
            transcript: Transcribed text from the consultation
            template: SOAP template defining expected structure
            language: Output language for the note (fr/de/en)

        Returns:
            SOAPNoteOutput with the 4 SOAP sections

        Raises:
            ValueError: If the response cannot be parsed as valid SOAP JSON
            Exception: If the Mistral API call fails
        """
        system_prompt = build_soap_system_prompt(language)
        user_prompt = build_soap_user_prompt(transcript, template, language)

        logger.info("Calling Mistral AI model=%s language=%s", self.model, language)

        response = await self.client.chat.complete_async(
            model=self.model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            temperature=0.3,
            max_tokens=2000,
            response_format={"type": "json_object"},
        )

        content = response.choices[0].message.content
        return self._parse_soap_response(content)

    def _parse_soap_response(self, content: str) -> SOAPNoteOutput:
        """Parse the Mistral JSON response into SOAPNoteOutput.

        Args:
            content: Raw JSON string from Mistral response

        Returns:
            SOAPNoteOutput with parsed sections

        Raises:
            ValueError: If JSON parsing fails or required fields are missing
        """
        try:
            data = json.loads(content)
        except json.JSONDecodeError as e:
            logger.error("Failed to parse Mistral response as JSON: %s", e)
            raise ValueError(f"Invalid JSON response from LLM: {e}") from e

        errors = validate_soap_json_structure(data)
        if errors:
            logger.error("SOAP validation errors: %s", errors)
            raise ValueError(f"Invalid SOAP response: {'; '.join(errors)}")

        return SOAPNoteOutput(
            subjective=data["subjective"],
            objective=data["objective"],
            assessment=data["assessment"],
            plan=data["plan"],
        )
