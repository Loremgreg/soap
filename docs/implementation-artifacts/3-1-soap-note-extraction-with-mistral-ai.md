# Story 3.1: SOAP Note Extraction with Mistral AI

Status: done

## Story

As a physiotherapist,
I want my recorded consultation to be automatically structured into a SOAP note,
So that I save time on documentation and get a professional clinical format.

## Acceptance Criteria

### AC1: Extraction LLM via Mistral AI

**Given** a completed transcription from Deepgram (Story 2.3)
**When** the backend processes the transcript
**Then** the transcript is sent to Mistral AI (mistral-large-2) with a structured prompt
**And** the prompt instructs extraction into 4 sections: Subjective, Objective, Assessment, Plan
**And** the response is parsed into structured JSON format

### AC2: Template SOAP Structuré

**Given** the SOAP note structure template
**When** the prompt is constructed
**Then** it references the structure defined in `docs/templates/physiotherapy-note-template.md`
**And** the output follows the 4-section format:
- **Subjective (S)**: Patient's reported symptoms, history, complaints, functional impact
- **Objective (O)**: Observable findings, measurements, physical examination results
- **Assessment (A)**: Clinical reasoning, diagnosis, contributing factors
- **Plan (P)**: Treatment provided, home program, follow-up plan

### AC3: Performance < 30 secondes

**Given** the Mistral API call
**When** generating the SOAP note
**Then** the total time from Stop button to note displayed is < 30 seconds
**And** latency is logged to metrics for monitoring (NFR11)

### AC4: Abstraction LLM Switchable

**Given** the LLM abstraction layer
**When** Mistral AI is called
**Then** the implementation uses an abstraction that can be switched to Azure OpenAI
**And** the switch requires only configuration change, not code change

### AC5: Gestion Multilingue

**Given** the transcript is in any language (FR/DE/EN/ES/other)
**When** the note is generated
**Then** the note is ALWAYS in the user's app language setting (not the transcript language)
**And** medical terminology is appropriate for the output language
**And** the LLM handles transcription-to-note language translation if needed

### AC6: Schéma Table Notes

**Given** the notes table schema
**When** a note is generated
**Then** the notes table is created with: id, user_id, recording_id, subjective, objective, assessment, plan, language, format (paragraph/bullets), verbosity (concise/medium), created_at, updated_at

### AC7: Gestion Erreurs

**Given** Mistral API fails or times out
**When** an error occurs
**Then** the error is logged to Sentry
**And** user sees a clear error message
**And** retry option is available
**And** the transcript is not lost (can retry extraction)

## Tasks / Subtasks

- [x] **Task 1: LLM Service Abstraction Layer** (AC: #4)
  - [x] 1.1 Créer l'interface abstraite `BaseLLMClient` dans `backend/app/services/llm/base.py`
  - [x] 1.2 Implémenter `MistralLLMClient` dans `backend/app/services/llm/mistral.py`
  - [x] 1.3 Créer factory `get_llm_client()` avec config `LLM_PROVIDER` env var
  - [x] 1.4 Ajouter placeholder `AzureOpenAIClient` (stub pour switch futur)
  - [x] 1.5 Tests unitaires pour la factory et l'abstraction

- [x] **Task 2: Prompt Engineering SOAP** (AC: #1, #2)
  - [x] 2.1 Créer module prompts dans `backend/app/services/llm/prompts/soap_extraction.py`
  - [x] 2.2 Implémenter `build_soap_system_prompt()` avec règles critiques
  - [x] 2.3 Implémenter `build_soap_user_prompt(transcript, template, language)`
  - [x] 2.4 Charger template depuis `docs/templates/physiotherapy-note-template.md`
  - [x] 2.5 Valider structure JSON output (4 sections obligatoires)

- [x] **Task 3: Modèle SQLAlchemy Notes** (AC: #6)
  - [x] 3.1 Créer modèle `Note` dans `backend/app/models/note.py`
  - [x] 3.2 Créer migration Alembic pour table `notes`
  - [x] 3.3 Créer schémas Pydantic `NoteCreate`, `NoteResponse`, `NoteUpdate`
  - [x] 3.4 Tests modèle et schémas

- [x] **Task 4: Service SOAP Extraction** (AC: #1, #3, #5)
  - [x] 4.1 Créer `SOAPExtractionService` dans `backend/app/services/soap_extraction.py`
  - [x] 4.2 Implémenter `extract_soap_note(transcript, user_language)` avec Mistral
  - [x] 4.3 Parser réponse JSON en structure `SOAPNote`
  - [x] 4.4 Ajouter timing/latency logging pour NFR11
  - [x] 4.5 Tests unitaires avec mocks Mistral

- [x] **Task 5: Endpoint API Génération Note** (AC: #1, #7)
  - [x] 5.1 Créer `POST /api/v1/notes` dans `backend/app/routers/notes.py`
  - [x] 5.2 Intégrer avec `recordings` (lien recording_id)
  - [x] 5.3 Implémenter retry logic avec tenacity (3 tentatives, backoff exponentiel)
  - [x] 5.4 Ajouter error handling avec codes erreur standardisés
  - [x] 5.5 Logging Sentry pour erreurs Mistral
  - [x] 5.6 Tests d'intégration endpoint

- [x] **Task 6: Validation & Tests E2E** (AC: tous)
  - [x] 6.1 Test flow complet: transcript → SOAP note
  - [x] 6.2 Valider performance < 30s (mock ou staging)
  - [x] 6.3 Test multilingue: FR/DE/EN transcripts → FR output
  - [x] 6.4 Test error handling: timeout, API failure

## Dev Notes

### Architecture Pattern: LLM Abstraction

```python
# backend/app/services/llm/base.py
from abc import ABC, abstractmethod
from pydantic import BaseModel

class SOAPNoteOutput(BaseModel):
    """Structure de sortie SOAP parsée."""
    subjective: str
    objective: str
    assessment: str
    plan: str

class BaseLLMClient(ABC):
    """Interface abstraite pour les providers LLM."""

    @abstractmethod
    async def extract_soap_note(
        self,
        transcript: str,
        template: str,
        language: str
    ) -> SOAPNoteOutput:
        """
        Extrait une note SOAP structurée depuis une transcription.

        Args:
            transcript: Texte transcrit de la consultation
            template: Template SOAP (4 sections)
            language: Langue de sortie de la note (fr/de/en)

        Returns:
            SOAPNoteOutput avec les 4 sections
        """
        pass
```

### Mistral AI SDK - Pattern Correct (v1.x)

**ATTENTION CRITIQUE**: Le SDK Mistral v1.x a changé d'API par rapport aux anciennes versions.

```python
# backend/app/services/llm/mistral.py
from mistralai import Mistral
import os

class MistralLLMClient(BaseLLMClient):
    """Client Mistral AI pour extraction SOAP."""

    def __init__(self):
        self.client = Mistral(api_key=os.getenv("MISTRAL_API_KEY"))
        self.model = "mistral-large-2"  # Meilleur modèle pour extraction structurée

    async def extract_soap_note(
        self,
        transcript: str,
        template: str,
        language: str
    ) -> SOAPNoteOutput:
        """Extrait une note SOAP via Mistral AI."""

        system_prompt = self._build_system_prompt(language)
        user_prompt = self._build_user_prompt(transcript, template)

        # SDK v1.x - méthode correcte
        response = await self.client.chat.complete_async(
            model=self.model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            temperature=0.3,  # Faible pour cohérence
            max_tokens=2000,
            response_format={"type": "json_object"}  # Force JSON output
        )

        content = response.choices[0].message.content
        return self._parse_soap_response(content)
```

### Règles Prompt SOAP Critiques

```python
SYSTEM_PROMPT_TEMPLATE = """Tu es un assistant médical expert en documentation clinique pour physiothérapeutes.

RÈGLES CRITIQUES:
1. Utilise UNIQUEMENT les informations présentes dans la transcription
2. N'INVENTE JAMAIS d'informations cliniques
3. Respecte STRICTEMENT la structure du template SOAP fourni
4. Génère la note en {language} (français/allemand/anglais selon paramètre)
5. Si une section manque d'informations, écris "Non documenté" ou "À compléter"
6. Utilise la terminologie médicale appropriée pour la langue de sortie

FORMAT DE SORTIE OBLIGATOIRE (JSON):
{{
    "subjective": "...",
    "objective": "...",
    "assessment": "...",
    "plan": "..."
}}
"""
```

### Schéma Table Notes

```sql
-- Migration Alembic
CREATE TABLE notes (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    recording_id UUID NOT NULL REFERENCES recordings(id) ON DELETE CASCADE,
    subjective TEXT NOT NULL,
    objective TEXT NOT NULL,
    assessment TEXT NOT NULL,
    plan TEXT NOT NULL,
    language VARCHAR(5) NOT NULL DEFAULT 'fr',  -- ISO code: fr, de, en
    format VARCHAR(20) NOT NULL DEFAULT 'paragraph',  -- paragraph | bullets
    verbosity VARCHAR(20) NOT NULL DEFAULT 'medium',  -- concise | medium
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_notes_user_id ON notes(user_id);
CREATE INDEX idx_notes_recording_id ON notes(recording_id);
```

### Gestion Erreurs Standardisée

```python
# Codes erreur à utiliser (de project-context.md)
# - INTERNAL_ERROR (500) - Erreur Mistral générique
# - SERVICE_UNAVAILABLE (503) - Mistral timeout/indisponible

from tenacity import retry, stop_after_attempt, wait_exponential

@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=2, max=10)
)
async def extract_with_retry(self, transcript: str, template: str, language: str):
    """Extraction avec retry automatique."""
    try:
        return await self.extract_soap_note(transcript, template, language)
    except Exception as e:
        # Log Sentry
        sentry_sdk.capture_exception(e)
        raise
```

### Learnings from Story 2.3 (Deepgram)

1. **Async obligatoire**: Utiliser `complete_async()` et non `complete()` pour ne pas bloquer
2. **Error handling robuste**: Tenacity pour retries, Sentry pour logging
3. **Timing metrics**: Logger latence pour NFR monitoring
4. **Tests avec mocks**: Ne pas appeler API réelle dans tests unitaires

### Project Structure Notes

**Fichiers à créer/modifier:**

```
backend/app/
├── models/
│   └── note.py                    # NOUVEAU - Modèle SQLAlchemy Note
├── schemas/
│   └── note.py                    # NOUVEAU - Pydantic schemas
├── services/
│   ├── llm/
│   │   ├── __init__.py           # NOUVEAU
│   │   ├── base.py               # NOUVEAU - Interface abstraite
│   │   ├── mistral.py            # NOUVEAU - Implémentation Mistral
│   │   └── prompts/
│   │       └── soap_extraction.py # NOUVEAU - Prompts SOAP
│   └── soap_extraction.py         # NOUVEAU - Service orchestration
├── routers/
│   └── notes.py                   # NOUVEAU - Endpoints API
└── core/
    └── config.py                  # MODIFIER - Ajouter MISTRAL_API_KEY, LLM_PROVIDER
```

**Dépendances Python à ajouter:**
```
mistralai>=1.0.0
tenacity>=8.0.0
```

### References

- [Source: docs/templates/physiotherapy-note-template.md] - Structure SOAP complète
- [Source: project-context.md#Mistral-AI] - Pattern extraction et abstraction LLM
- [Source: docs/planning-artifacts/architecture/implementation-patterns-coding-standards.md] - Conventions nommage, error handling
- [Source: docs/implementation-artifacts/2-3-deepgram-streaming-integration.md] - Learnings async, retry, Sentry
- [Source: docs/planning-artifacts/epics/stories.md#Story-3.1] - Acceptance criteria originaux

### Variables d'Environnement Requises

```bash
MISTRAL_API_KEY=xxx          # Clé API Mistral AI
LLM_PROVIDER=mistral         # Provider actif (mistral | azure_openai)
```

### Performance NFR11

- **Cible**: < 30 secondes de Stop button à note affichée
- **Breakdown estimé**:
  - Transcription Deepgram: ~5s (Story 2.3)
  - Extraction Mistral: ~10-20s
  - Parsing + DB save: ~1s
- **Logging**: Utiliser `time.perf_counter()` pour mesurer latence Mistral

## Dev Agent Record

### Agent Model Used

Claude Opus 4.6 (claude-opus-4-6)

### Debug Log References

- Test suite: 165/174 passing (9 pre-existing failures in subscription/plans timezone handling, unrelated to this story)
- New tests added: 59 tests across 5 test files, all passing
- No regressions introduced
- Code review fixes applied: 7 issues fixed (3 HIGH, 4 MEDIUM)

### Completion Notes List

- **Task 1**: Implemented LLM abstraction layer with `BaseLLMClient` ABC, `MistralLLMClient` using SDK v1.x async API, `AzureOpenAILLMClient` stub, and factory pattern via `get_llm_client()`. Switch between providers requires only `LLM_PROVIDER` env var change.
- **Task 2**: Created dedicated prompt module with `build_soap_system_prompt()`, `build_soap_user_prompt()`, `load_soap_template()`, and `validate_soap_json_structure()`. System prompt enforces 6 critical rules including no fabrication of clinical data and mandatory JSON output format.
- **Task 3**: Created `Note` SQLAlchemy model with all required columns (id, user_id, recording_id, subjective, objective, assessment, plan, language, format, verbosity, created_at, updated_at). Created Alembic migration `c3d4e5f6g7h8`. Created Pydantic schemas with camelCase serialization.
- **Task 4**: Created `SOAPExtractionService` with `extract_soap_note()` and `create_note_from_transcript()` functions. Includes tenacity retry (3 attempts, exponential backoff), `time.perf_counter()` latency measurement for NFR11, Sentry error logging, and 25s latency warning threshold.
- **Task 5**: Created `POST /api/v1/soap-notes` endpoint with recording ownership validation, transcript availability check, error handling with NoteGenerationFailedException (500), and Sentry integration.
- **Task 6**: Comprehensive E2E tests covering full extraction flow, 4-section validation, performance verification, multilingual support (FR/DE/EN), error handling (timeout, API failure), and transcript preservation on failure.

### Change Log

- 2026-02-07: Implemented Story 3.1 - SOAP Note Extraction with Mistral AI (all 6 tasks, 7 ACs satisfied)
- 2026-02-10: Code review fixes — renamed table `notes`→`soap_notes`, endpoint `/notes`→`/soap-notes`, added Literal validation for language/format/verbosity, fixed LLM client instantiation per retry, used language in user prompt, removed dead LLMServiceUnavailableException, deleted junk file `backend/=1.0.0`

### File List

**New files:**
- backend/app/services/llm/__init__.py
- backend/app/services/llm/base.py
- backend/app/services/llm/mistral.py
- backend/app/services/llm/azure_openai.py
- backend/app/services/llm/factory.py
- backend/app/services/llm/prompts/__init__.py
- backend/app/services/llm/prompts/soap_extraction.py
- backend/app/services/soap_extraction.py
- backend/app/models/note.py
- backend/app/schemas/note.py
- backend/app/routers/notes.py
- backend/alembic/versions/c3d4e5f6g7h8_create_notes_table.py
- backend/app/tests/test_llm_service.py
- backend/app/tests/test_note_model.py
- backend/app/tests/test_soap_extraction_service.py
- backend/app/tests/test_notes_endpoint.py
- backend/app/tests/test_soap_e2e.py

**Modified files:**
- backend/app/main.py (added notes router)
- backend/app/models/__init__.py (added Note export)
- backend/app/schemas/__init__.py (added note schema exports)
- backend/app/services/__init__.py (added soap_extraction export)
- backend/requirements.txt (added mistralai>=1.0.0)
- docs/implementation-artifacts/sprint-status.yaml (status update)
- docs/implementation-artifacts/3-1-soap-note-extraction-with-mistral-ai.md (this file)
