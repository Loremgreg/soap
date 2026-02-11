"""LLM service abstraction layer for SOAP note extraction."""

from app.services.llm.base import BaseLLMClient, SOAPNoteOutput
from app.services.llm.factory import get_llm_client

__all__ = ["BaseLLMClient", "SOAPNoteOutput", "get_llm_client"]
