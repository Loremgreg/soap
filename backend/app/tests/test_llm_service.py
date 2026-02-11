"""Tests for the LLM service abstraction layer.

Tests cover:
- BaseLLMClient interface and SOAPNoteOutput model
- MistralLLMClient response parsing and API calls
- AzureOpenAILLMClient placeholder behavior
- Factory function with provider selection
- Prompt building and template loading functions
"""

import json
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from app.services.llm.base import BaseLLMClient, SOAPNoteOutput
from app.services.llm.azure_openai import AzureOpenAILLMClient
from app.services.llm.factory import get_llm_client
from app.services.llm.mistral import MistralLLMClient
from app.services.llm.prompts.soap_extraction import (
    build_soap_system_prompt,
    build_soap_user_prompt,
    load_soap_template,
    validate_soap_json_structure,
)


# ─── SOAPNoteOutput Model Tests ───────────────────────────────────────────────


class TestSOAPNoteOutput:
    """Tests for the SOAPNoteOutput Pydantic model."""

    def test_create_valid_output(self):
        """SOAPNoteOutput should accept all 4 required fields."""
        output = SOAPNoteOutput(
            subjective="Patient reports knee pain",
            objective="ROM limited to 90 degrees flexion",
            assessment="Acute patellofemoral syndrome",
            plan="Ice 3x/day, exercises prescribed",
        )
        assert output.subjective == "Patient reports knee pain"
        assert output.objective == "ROM limited to 90 degrees flexion"
        assert output.assessment == "Acute patellofemoral syndrome"
        assert output.plan == "Ice 3x/day, exercises prescribed"

    def test_missing_field_raises_error(self):
        """SOAPNoteOutput should reject missing required fields."""
        with pytest.raises(Exception):
            SOAPNoteOutput(
                subjective="Pain",
                objective="Swelling",
                assessment="Inflammation",
                # plan is missing
            )


# ─── BaseLLMClient Interface Tests ────────────────────────────────────────────


class TestBaseLLMClient:
    """Tests for the abstract BaseLLMClient interface."""

    def test_cannot_instantiate_abstract_class(self):
        """BaseLLMClient cannot be instantiated directly."""
        with pytest.raises(TypeError):
            BaseLLMClient()

    def test_subclass_must_implement_extract(self):
        """Subclasses missing extract_soap_note should raise TypeError."""

        class IncompleteClient(BaseLLMClient):
            pass

        with pytest.raises(TypeError):
            IncompleteClient()


# ─── Prompt Module Tests ──────────────────────────────────────────────────────


class TestBuildSoapSystemPrompt:
    """Tests for the system prompt builder."""

    def test_french_prompt(self):
        """System prompt should include French language instruction."""
        prompt = build_soap_system_prompt("fr")
        assert "français" in prompt
        assert "UNIQUEMENT" in prompt
        assert "N'INVENTE JAMAIS" in prompt
        assert '"subjective"' in prompt

    def test_german_prompt(self):
        """System prompt should include German language instruction."""
        prompt = build_soap_system_prompt("de")
        assert "allemand" in prompt or "deutsch" in prompt

    def test_english_prompt(self):
        """System prompt should include English language instruction."""
        prompt = build_soap_system_prompt("en")
        assert "anglais" in prompt or "english" in prompt

    def test_unknown_language_uses_code(self):
        """Unknown language code should be used as-is."""
        prompt = build_soap_system_prompt("it")
        assert "it" in prompt


class TestBuildSoapUserPrompt:
    """Tests for the user prompt builder."""

    def test_includes_transcript_and_template(self):
        """User prompt should include transcript and template."""
        prompt = build_soap_user_prompt(
            transcript="Le patient dit avoir mal au genou",
            template="## Subjective\n## Objective",
            language="fr",
        )
        assert "Le patient dit avoir mal au genou" in prompt
        assert "## Subjective" in prompt

    def test_includes_json_instruction(self):
        """User prompt should instruct JSON-only response."""
        prompt = build_soap_user_prompt("transcript", "template", "fr")
        assert "JSON" in prompt

    def test_includes_language_in_prompt(self):
        """User prompt should mention the target language."""
        prompt = build_soap_user_prompt("transcript", "template", "de")
        assert "allemand" in prompt or "deutsch" in prompt


class TestValidateSoapJsonStructure:
    """Tests for SOAP JSON validation."""

    def test_valid_structure(self):
        """Valid SOAP structure should return no errors."""
        data = {
            "subjective": "Pain",
            "objective": "Swelling",
            "assessment": "Sprain",
            "plan": "Rest",
        }
        assert validate_soap_json_structure(data) == []

    def test_missing_fields(self):
        """Missing fields should return error messages."""
        data = {"subjective": "Pain", "objective": "Swelling"}
        errors = validate_soap_json_structure(data)
        assert len(errors) > 0
        assert any("Missing" in e for e in errors)

    def test_empty_field(self):
        """Empty string field should return error."""
        data = {
            "subjective": "",
            "objective": "Swelling",
            "assessment": "Sprain",
            "plan": "Rest",
        }
        errors = validate_soap_json_structure(data)
        assert any("empty" in e for e in errors)

    def test_non_string_field(self):
        """Non-string field should return error."""
        data = {
            "subjective": 123,
            "objective": "Swelling",
            "assessment": "Sprain",
            "plan": "Rest",
        }
        errors = validate_soap_json_structure(data)
        assert any("string" in e for e in errors)


class TestLoadSoapTemplate:
    """Tests for SOAP template file loading."""

    def test_load_existing_template(self, tmp_path):
        """Should load template content from file."""
        template_dir = tmp_path / "docs" / "templates"
        template_dir.mkdir(parents=True)
        template_file = template_dir / "physiotherapy-note-template.md"
        template_file.write_text("## Subjective\n## Objective\n")

        content = load_soap_template(tmp_path)
        assert "## Subjective" in content

    def test_missing_template_raises_error(self, tmp_path):
        """Should raise FileNotFoundError if template doesn't exist."""
        with pytest.raises(FileNotFoundError, match="SOAP template not found"):
            load_soap_template(tmp_path)


# ─── MistralLLMClient Tests ───────────────────────────────────────────────────


class TestMistralLLMClient:
    """Tests for MistralLLMClient implementation."""

    @patch("app.services.llm.mistral.get_settings")
    @patch("app.services.llm.mistral.Mistral")
    def test_init_creates_client(self, mock_mistral_cls, mock_settings):
        """MistralLLMClient should initialize with API key from settings."""
        mock_settings.return_value.mistral_api_key = "test-key"

        client = MistralLLMClient()

        mock_mistral_cls.assert_called_once_with(api_key="test-key")
        assert client.model == "mistral-large-2"

    @patch("app.services.llm.mistral.get_settings")
    @patch("app.services.llm.mistral.Mistral")
    def test_parse_valid_response(self, mock_mistral_cls, mock_settings):
        """Valid JSON response should be parsed into SOAPNoteOutput."""
        mock_settings.return_value.mistral_api_key = "test-key"
        client = MistralLLMClient()

        valid_json = json.dumps({
            "subjective": "Douleur genou droit",
            "objective": "Flexion limitée à 90°",
            "assessment": "Syndrome fémoro-patellaire",
            "plan": "Glace 3x/jour",
        })

        result = client._parse_soap_response(valid_json)

        assert isinstance(result, SOAPNoteOutput)
        assert result.subjective == "Douleur genou droit"
        assert result.plan == "Glace 3x/jour"

    @patch("app.services.llm.mistral.get_settings")
    @patch("app.services.llm.mistral.Mistral")
    def test_parse_invalid_json_raises_error(self, mock_mistral_cls, mock_settings):
        """Invalid JSON should raise ValueError."""
        mock_settings.return_value.mistral_api_key = "test-key"
        client = MistralLLMClient()

        with pytest.raises(ValueError, match="Invalid JSON"):
            client._parse_soap_response("not valid json {{{")

    @patch("app.services.llm.mistral.get_settings")
    @patch("app.services.llm.mistral.Mistral")
    def test_parse_missing_fields_raises_error(self, mock_mistral_cls, mock_settings):
        """JSON missing required SOAP fields should raise ValueError."""
        mock_settings.return_value.mistral_api_key = "test-key"
        client = MistralLLMClient()

        incomplete_json = json.dumps({
            "subjective": "Pain",
            "objective": "Swelling",
            # missing assessment and plan
        })

        with pytest.raises(ValueError, match="Invalid SOAP response"):
            client._parse_soap_response(incomplete_json)

    @pytest.mark.asyncio
    @patch("app.services.llm.mistral.get_settings")
    @patch("app.services.llm.mistral.Mistral")
    async def test_extract_soap_note_calls_api(self, mock_mistral_cls, mock_settings):
        """extract_soap_note should call Mistral API with correct parameters."""
        mock_settings.return_value.mistral_api_key = "test-key"

        mock_response = MagicMock()
        mock_response.choices = [
            MagicMock(
                message=MagicMock(
                    content=json.dumps({
                        "subjective": "Douleur",
                        "objective": "Gonflement",
                        "assessment": "Entorse",
                        "plan": "Repos",
                    })
                )
            )
        ]
        mock_client_instance = MagicMock()
        mock_client_instance.chat.complete_async = AsyncMock(
            return_value=mock_response
        )
        mock_mistral_cls.return_value = mock_client_instance

        client = MistralLLMClient()
        result = await client.extract_soap_note(
            transcript="Le patient a mal",
            template="## Template",
            language="fr",
        )

        assert isinstance(result, SOAPNoteOutput)
        assert result.subjective == "Douleur"

        mock_client_instance.chat.complete_async.assert_called_once()
        call_kwargs = mock_client_instance.chat.complete_async.call_args[1]
        assert call_kwargs["model"] == "mistral-large-2"
        assert call_kwargs["temperature"] == 0.3
        assert call_kwargs["response_format"] == {"type": "json_object"}


# ─── AzureOpenAILLMClient Tests ───────────────────────────────────────────────


class TestAzureOpenAILLMClient:
    """Tests for the Azure OpenAI placeholder implementation."""

    @pytest.mark.asyncio
    async def test_raises_not_implemented(self):
        """Azure OpenAI stub should raise NotImplementedError."""
        client = AzureOpenAILLMClient()

        with pytest.raises(NotImplementedError, match="not yet implemented"):
            await client.extract_soap_note(
                transcript="test",
                template="test",
                language="fr",
            )

    def test_is_base_llm_client_subclass(self):
        """AzureOpenAILLMClient should be a valid BaseLLMClient subclass."""
        assert issubclass(AzureOpenAILLMClient, BaseLLMClient)


# ─── Factory Tests ────────────────────────────────────────────────────────────


class TestGetLLMClient:
    """Tests for the LLM client factory function."""

    @patch("app.services.llm.factory.get_settings")
    @patch("app.services.llm.mistral.get_settings")
    @patch("app.services.llm.mistral.Mistral")
    def test_returns_mistral_by_default(
        self, mock_mistral_cls, mock_mistral_settings, mock_factory_settings
    ):
        """Factory should return MistralLLMClient when provider is 'mistral'."""
        mock_factory_settings.return_value.llm_provider = "mistral"
        mock_mistral_settings.return_value.mistral_api_key = "test-key"

        client = get_llm_client()

        assert isinstance(client, MistralLLMClient)

    @patch("app.services.llm.factory.get_settings")
    def test_returns_azure_openai(self, mock_settings):
        """Factory should return AzureOpenAILLMClient when configured."""
        mock_settings.return_value.llm_provider = "azure_openai"

        client = get_llm_client()

        assert isinstance(client, AzureOpenAILLMClient)

    @patch("app.services.llm.factory.get_settings")
    def test_raises_for_unknown_provider(self, mock_settings):
        """Factory should raise ValueError for unsupported providers."""
        mock_settings.return_value.llm_provider = "unsupported_provider"

        with pytest.raises(ValueError, match="Unsupported LLM provider"):
            get_llm_client()
