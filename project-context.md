# Project Context - SOAP Notice

> Ce fichier contient les règles critiques et patterns de code que les agents AI DOIVENT suivre lors de l'implémentation.

## Projet

**Nom:** SOAP Notice
**Description:** Application de transcription audio pour physiothérapeutes - transforme des enregistrements d'anamnèses en notes SOAP structurées.

---

## Stack Technique Complète

| Composant | Technologie |
|-----------|-------------|
| **Frontend** | Vite + React + TypeScript + TailwindCSS + shadcn/ui |
| **State Management** | Zustand (état local) + TanStack Query (données serveur) |
| **Routing** | TanStack Router |
| **Forms** | React Hook Form |
| **Audio Capture** | Web Audio API native |
| **Backend** | Python FastAPI (async) |
| **ORM** | SQLAlchemy 2.0 async |
| **Migrations** | Alembic |
| **Validation** | Pydantic v2 |
| **Auth** | Authlib + JWT + httpOnly Cookie |
| **Database** | Neon (PostgreSQL serverless EU) |
| **STT** | Deepgram API (nova-3, WebSocket) |
| **LLM** | Mistral AI (abstraction switchable vers Azure OpenAI) |
| **Payments** | Stripe |
| **Hosting Frontend** | Vercel |
| **Hosting Backend** | Railway (EU region) |
| **Monitoring** | Sentry |

---

## Coding Standards - OBLIGATOIRES

### Documentation

**RÈGLE CRITIQUE:** JSDoc (TypeScript) et Docstrings (Python) sur TOUTES les fonctions, interfaces et classes publiques.

**Format JSDoc (Frontend):**
```typescript
/**
 * Description de la fonction.
 *
 * @param paramName - Description du paramètre
 * @returns Description du retour
 */
export function myFunction(paramName: string): ReturnType {
  // ...
}
```

**Format Docstring (Backend):**
```python
def my_function(param_name: str) -> ReturnType:
    """
    Description de la fonction.

    Args:
        param_name: Description du paramètre

    Returns:
        Description du retour
    """
    pass
```

### Conventions de Nommage

| Contexte | Convention | Exemple |
|----------|------------|---------|
| **Tables/Colonnes DB** | snake_case | `soap_notes`, `user_id`, `created_at` |
| **Endpoints API** | Pluriel + kebab-case | `/api/v1/soap-notes`, `/api/v1/users` |
| **Composants React** | PascalCase | `RecordButton.tsx`, `SOAPEditor.tsx` |
| **Fichiers React** | PascalCase | `RecordButton.tsx` |
| **Hooks React** | camelCase + use | `useRecording.ts`, `useQuota.ts` |
| **Fonctions TS** | camelCase | `formatDate()`, `handleSubmit()` |
| **Variables TS** | camelCase | `isRecording`, `currentNote` |
| **Constantes** | SCREAMING_SNAKE_CASE | `MAX_RECORDING_TIME` |
| **Types/Interfaces** | PascalCase | `SOAPNote`, `UserQuota` |
| **Fichiers Python** | snake_case | `soap_notes.py` |
| **Classes Python** | PascalCase | `SOAPNote`, `UserService` |
| **Fonctions Python** | snake_case | `get_user_quota()` |
| **JSON fields (API)** | camelCase | `createdAt`, `userId` |

### Git Commits

Format: Conventional Commits
```
feat(recording): add pause/resume functionality
fix(auth): handle expired JWT token gracefully
docs(api): add endpoint documentation
refactor(notes): extract SOAP formatting to service
test(quota): add unit tests for quota calculation
chore(deps): update TanStack Query to v5.18
```

---

## Structure Projet

### Frontend (`/frontend/src/`)

```
src/
├── features/           # Par fonctionnalité
│   ├── auth/          # components/, hooks/, pages/
│   ├── recording/     # components/, hooks/, pages/
│   ├── notes/         # components/, hooks/, pages/
│   ├── billing/       # components/, hooks/, pages/
│   └── settings/      # components/, pages/
├── components/        # Composants partagés
│   ├── ui/           # shadcn/ui components
│   └── layout/       # Header, BottomNav, etc.
├── hooks/            # Hooks partagés
├── lib/              # Utilitaires (api.ts, utils.ts)
├── types/            # Types globaux
└── routes/           # TanStack Router
```

### Backend (`/backend/app/`)

```
app/
├── routers/          # Endpoints API par domaine
├── services/         # Logique métier
├── models/           # SQLAlchemy ORM
├── schemas/          # Pydantic request/response
├── core/             # database.py, security.py, exceptions.py
└── tests/            # Tests co-located
```

### Tests

**RÈGLE:** Tests co-located avec le code source.
```
RecordButton/
├── RecordButton.tsx
├── RecordButton.test.tsx   # Test à côté
└── index.ts
```

---

## API Patterns

### Versioning

Toutes les routes API commencent par `/api/v1/`

### Format Réponse Succès

Format direct (pas de wrapper):
```json
{ "id": "abc", "subjective": "...", "createdAt": "2026-01-17T10:30:00Z" }
```

### Format Erreur

```json
{
  "error": {
    "code": "QUOTA_EXCEEDED",
    "message": "Vous avez atteint votre quota mensuel",
    "details": { "used": 50, "limit": 50 }
  }
}
```

**Codes d'erreur:**
- `INVALID_REQUEST` (400)
- `VALIDATION_ERROR` (400)
- `UNAUTHORIZED` (401)
- `QUOTA_EXCEEDED` (403)
- `TRIAL_EXPIRED` (403)
- `NOT_FOUND` (404)
- `AUDIO_TOO_LONG` (413)
- `RATE_LIMITED` (429)
- `INTERNAL_ERROR` (500)
- `SERVICE_UNAVAILABLE` (503)

### Dates

- **API (JSON):** ISO 8601 UTC → `2026-01-17T10:30:00Z`
- **Database:** TIMESTAMP WITH TIME ZONE
- **UI:** Localisé selon langue utilisateur

---

## Frontend Patterns

### State Management

```typescript
// Zustand pour état local
const useStore = create((set) => ({
  isRecording: false,
  startRecording: () => set({ isRecording: true }),
}));

// TanStack Query pour données serveur
const { data, isLoading } = useQuery({
  queryKey: ['notes'],
  queryFn: fetchNotes
});
```

### Loading States Pattern

```tsx
if (error) return <ErrorMessage error={error} />;
if (isLoading) return <Skeleton />;
if (data.length === 0) return <EmptyState />;
return <DataList data={data} />;
```

### Error Handling

- Erreur réseau → Toast + retry automatique (TanStack Query)
- Erreur validation → Message inline sous le champ
- Erreur quota → Modal avec CTA upgrade
- Erreur serveur → Toast + log Sentry

---

## Deepgram - Règles Critiques

### Installation SDK Python

```bash
pip install deepgram-sdk httpx
```

### Modèle et Langues Supportées

- **Modèle recommandé:** `nova-3` (meilleure précision, multilingue)
- **Langues requises:** Français, Allemand, Anglais

| Langue | Code Deepgram | Statut Nova-3 |
|--------|---------------|---------------|
| Français | `fr`, `fr-CA` | Supporté |
| Allemand | `de`, `de-CH` | Supporté |
| Anglais | `en`, `en-US`, `en-GB` | Supporté |
| Multilingue auto | `multi` | Détection automatique |

```python
# Configuration multilingue
model = "nova-3"
language = "multi"  # Détection automatique de la langue
smart_format = True
```

### Pattern de Transcription Live (WebSocket)

```python
import httpx
import threading
from deepgram import DeepgramClient
from deepgram.core.events import EventType
from deepgram.extensions.types.sockets import ListenV1SocketClientResponse

def transcribe_audio_stream(audio_source_url: str) -> None:
    """
    Transcrit un flux audio en temps réel via Deepgram WebSocket.

    Args:
        audio_source_url: URL du flux audio à transcrire

    Note:
        La clé API doit être dans DEEPGRAM_API_KEY (env var)
    """
    deepgram = DeepgramClient()

    with deepgram.listen.v1.connect(
        model="nova-3",
        language="multi",
        smart_format=True,
        punctuate=True,
    ) as connection:

        def on_message(message: ListenV1SocketClientResponse) -> None:
            """Callback pour chaque résultat de transcription."""
            if hasattr(message, 'channel') and hasattr(message.channel, 'alternatives'):
                transcript = message.channel.alternatives[0].transcript
                if transcript:
                    print(f"Transcription: {transcript}")

        connection.on(EventType.OPEN, lambda _: print("Connexion Deepgram ouverte"))
        connection.on(EventType.MESSAGE, on_message)
        connection.on(EventType.CLOSE, lambda _: print("Connexion fermée"))
        connection.on(EventType.ERROR, lambda err: print(f"Erreur: {err}"))

        def listening_thread():
            connection.start_listening()

        listen_thread = threading.Thread(target=listening_thread)
        listen_thread.start()

        def stream_audio():
            with httpx.stream("GET", audio_source_url) as response:
                for chunk in response.iter_bytes():
                    connection.send_media(chunk)

        audio_thread = threading.Thread(target=stream_audio)
        audio_thread.start()

        audio_thread.join()
        listen_thread.join()
```

### Paramètres WebSocket Importants

| Paramètre | Valeur | Description |
|-----------|--------|-------------|
| `model` | `nova-3` | Meilleur modèle pour le français |
| `language` | `fr` | Français |
| `smart_format` | `true` | Formate nombres, dates, emails |
| `punctuate` | `true` | Ajoute la ponctuation |
| `interim_results` | `false` | Résultats finaux uniquement (défaut) |
| `endpointing` | `300` | Délai fin de phrase en ms (optionnel) |

---

## Mistral AI - Extraction SOAP

### Installation SDK Python

```bash
pip install mistralai
```

### Pattern d'Extraction SOAP

```python
from mistralai.client import MistralClient
import os

def extract_soap_note(transcript: str, template: str, language: str = "fr") -> str:
    """
    Extrait une note SOAP structurée à partir d'une transcription.

    Args:
        transcript: Texte transcrit de l'anamnèse
        template: Template SOAP (4 sections)
        language: Langue de la note (fr, de, en)

    Returns:
        Note SOAP formatée en markdown
    """
    client = MistralClient(api_key=os.getenv("MISTRAL_API_KEY"))

    system_prompt = f"""Tu es un assistant médical expert en documentation clinique.
Extrais les informations de la transcription et structure-les selon le template SOAP fourni.

Règles CRITIQUES:
- Utilise UNIQUEMENT les informations présentes dans la transcription
- N'invente JAMAIS d'informations cliniques
- Respecte strictement la structure du template
- Génère la note en {language}
- Si une section manque d'informations, écris "Non documenté" ou "À compléter"
"""

    user_prompt = f"""Template SOAP:
{template}

Transcription de l'anamnèse:
{transcript}

Génère la note SOAP complète en respectant strictement le template."""

    response = client.chat(
        model="mistral-large-2",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ],
        temperature=0.3,
        max_tokens=2000
    )

    return response.choices[0].message.content
```

### Architecture Switchable LLM

```python
from abc import ABC, abstractmethod
from enum import Enum
import os

class LLMProvider(Enum):
    MISTRAL = "mistral"
    AZURE_OPENAI = "azure_openai"

class BaseLLMClient(ABC):
    @abstractmethod
    def extract_soap_note(self, transcript: str, template: str, language: str) -> str:
        """Extrait une note SOAP depuis une transcription."""
        pass

def get_llm_client() -> BaseLLMClient:
    """Factory pour obtenir le client LLM configuré."""
    provider = LLMProvider(os.getenv("LLM_PROVIDER", "mistral"))
    if provider == LLMProvider.MISTRAL:
        return MistralClient()
    elif provider == LLMProvider.AZURE_OPENAI:
        return AzureOpenAIClient()
```

### Paramètres Critiques

| Paramètre | Valeur | Justification |
|-----------|--------|---------------|
| `model` | `mistral-large-2` | Meilleur modèle Mistral pour extraction structurée |
| `temperature` | `0.3` | Faible = cohérence et précision (pas de créativité) |
| `max_tokens` | `2000` | Suffisant pour note SOAP complète |

---

## Contraintes Projet

### RGPD / Données de Santé
- Serveurs EU uniquement (Neon Frankfurt, Railway EU)
- Pas de stockage permanent des audio (transcription uniquement)
- Chiffrement des données en transit (TLS 1.3) et au repos

### Performance
- Latence totale < 30s après Stop
- 99% uptime cible

### Multilingue
- Langues MVP: Français, Allemand, Anglais
- Espagnol: Post-MVP (Phase 2)
- Détection automatique disponible (`multi`)

---

## Variables d'Environnement

```bash
# Database
DATABASE_URL=postgresql://...

# Auth
GOOGLE_CLIENT_ID=xxx
GOOGLE_CLIENT_SECRET=xxx
JWT_SECRET_KEY=xxx

# External Services
DEEPGRAM_API_KEY=xxx
MISTRAL_API_KEY=xxx
LLM_PROVIDER=mistral

# Payments
STRIPE_SECRET_KEY=xxx
STRIPE_WEBHOOK_SECRET=xxx

# Monitoring
SENTRY_DSN=xxx

# App Config
APP_ENV=development
API_BASE_URL=http://localhost:8000
FRONTEND_URL=http://localhost:5173
```

---

## Règles de Sécurité

**INTERDIT:**
- Clés API dans le code → Variables d'environnement
- `console.log` de tokens/passwords → Logger uniquement les IDs
- SQL brut avec concaténation → SQLAlchemy ORM
- `.env` dans Git → `.env.example` avec placeholders

---

## Format de Sortie SOAP

Le template cible pour l'extraction LLM se trouve dans:
`docs/templates/physiotherapy-note-template.md`

Sections principales:
1. **Subjective Assessment** - Plainte, historique, impact fonctionnel
2. **Objective Assessment** - Observations, examen physique
3. **Clinical Reasoning** - Diagnostic, mesures
4. **Management Plan** - Traitement, programme domicile, suivi
