"""SOAP note extraction prompt templates.

Contains system and user prompt builders for extracting structured
SOAP notes from physiotherapy consultation transcripts.
"""

import logging
from pathlib import Path

logger = logging.getLogger(__name__)

# Language code to display name mapping
LANGUAGE_NAMES: dict[str, str] = {
    "fr": "français",
    "de": "allemand/deutsch",
    "en": "anglais/english",
    "es": "español",
}

# Path to the SOAP template file (relative to project root)
TEMPLATE_RELATIVE_PATH = "docs/templates/physiotherapy-note-template.md"


def build_soap_system_prompt(language: str) -> str:
    """Build the system prompt for SOAP note extraction.

    The system prompt instructs the LLM to act as a medical documentation
    expert, with critical rules about accuracy and output format.

    Args:
        language: Output language code (fr/de/en)

    Returns:
        System prompt string with language-specific instructions
    """
    lang_name = LANGUAGE_NAMES.get(language, language)

    return (
        "Tu es un assistant médical expert en documentation clinique "
        "pour physiothérapeutes.\n\n"
        "RÈGLES CRITIQUES:\n"
        "1. Utilise UNIQUEMENT les informations présentes dans la transcription\n"
        "2. N'INVENTE JAMAIS d'informations cliniques\n"
        "3. Respecte STRICTEMENT la structure du template SOAP fourni\n"
        f"4. Génère la note en {lang_name}\n"
        "5. Si une section manque d'informations, écris "
        '"Non documenté" ou "À compléter"\n'
        "6. Utilise la terminologie médicale appropriée pour la langue de sortie\n\n"
        "FORMAT DE SORTIE OBLIGATOIRE (JSON):\n"
        "{\n"
        '    "subjective": "...",\n'
        '    "objective": "...",\n'
        '    "assessment": "...",\n'
        '    "plan": "..."\n'
        "}"
    )


def build_soap_user_prompt(transcript: str, template: str, language: str) -> str:
    """Build the user prompt with transcript and template.

    Args:
        transcript: Consultation transcript text
        template: SOAP template structure content
        language: Output language code (fr/de/en)

    Returns:
        User prompt string combining template and transcript
    """
    lang_name = LANGUAGE_NAMES.get(language, language)

    return (
        f"Template SOAP:\n{template}\n\n"
        f"Transcription de la consultation:\n{transcript}\n\n"
        f"Génère la note SOAP complète en {lang_name} en respectant "
        "strictement le template. "
        "Réponds UNIQUEMENT avec le JSON structuré."
    )


def load_soap_template(project_root: str | Path) -> str:
    """Load the SOAP template from the project's template file.

    Args:
        project_root: Absolute path to the project root directory

    Returns:
        Content of the physiotherapy note template

    Raises:
        FileNotFoundError: If the template file does not exist
    """
    template_path = Path(project_root) / TEMPLATE_RELATIVE_PATH
    if not template_path.exists():
        raise FileNotFoundError(
            f"SOAP template not found at: {template_path}"
        )

    content = template_path.read_text(encoding="utf-8")
    logger.info("Loaded SOAP template from %s (%d chars)", template_path, len(content))
    return content


def validate_soap_json_structure(data: dict) -> list[str]:
    """Validate that a parsed JSON dict contains required SOAP fields.

    Args:
        data: Parsed JSON dictionary from LLM response

    Returns:
        List of error messages (empty if valid)
    """
    errors: list[str] = []
    required_fields = {"subjective", "objective", "assessment", "plan"}
    missing = required_fields - set(data.keys())

    if missing:
        errors.append(f"Missing required SOAP fields: {missing}")

    for field in required_fields & set(data.keys()):
        if not isinstance(data[field], str):
            errors.append(f"Field '{field}' must be a string, got {type(data[field]).__name__}")
        elif not data[field].strip():
            errors.append(f"Field '{field}' is empty")

    return errors
