# Implementation Patterns & Coding Standards

## Documentation Requirements

**Règle obligatoire :** JSDoc (TypeScript) et Docstrings (Python) sur toutes les fonctions, interfaces et classes publiques.

**Format JSDoc (Frontend) :**
```typescript
/**
 * Description de la fonction.
 *
 * @param paramName - Description du paramètre
 * @returns Description du retour
 */
```

**Format Docstring (Backend) :**
```python
"""
Description de la fonction.

Args:
    param_name: Description du paramètre

Returns:
    Description du retour
"""
```

## Naming Conventions

| Contexte | Convention | Exemple |
|----------|------------|---------|
| **Tables/Colonnes DB** | snake_case | `soap_notes`, `user_id`, `created_at` |
| **Endpoints API** | Pluriel + kebab-case | `/api/v1/soap-notes`, `/api/v1/users` |
| **Composants React** | PascalCase | `RecordButton.tsx`, `SOAPEditor.tsx` |
| **Fichiers React** | PascalCase | `RecordButton.tsx` |
| **Hooks React** | camelCase + use | `useRecording.ts`, `useQuota.ts` |
| **Fonctions TS** | camelCase | `formatDate()`, `handleSubmit()` |
| **Variables TS** | camelCase | `isRecording`, `currentNote` |
| **Constantes** | SCREAMING_SNAKE_CASE | `MAX_RECORDING_TIME`, `API_BASE_URL` |
| **Types/Interfaces** | PascalCase | `SOAPNote`, `UserQuota` |
| **Fichiers Python** | snake_case | `soap_notes.py`, `deepgram_service.py` |
| **Classes Python** | PascalCase | `SOAPNote`, `UserService` |
| **Fonctions Python** | snake_case | `get_user_quota()`, `create_note()` |
| **JSON fields (API)** | camelCase | `createdAt`, `userId` |

## Project Structure

**Tests :** Co-located avec le code source

```
src/components/RecordButton/
├── RecordButton.tsx
├── RecordButton.test.tsx   # Test à côté du composant
└── index.ts
```

**Frontend :** Structure hybride (features + shared)

```
src/
├── features/           # Par fonctionnalité (recording/, notes/, auth/)
├── components/         # Composants partagés (ui/, layout/)
├── hooks/              # Hooks partagés
├── lib/                # Utilitaires
└── types/              # Types globaux
```

**Backend :** Structure par domaine

```
app/
├── routers/            # Endpoints API par domaine
├── services/           # Logique métier
├── models/             # SQLAlchemy ORM
├── schemas/            # Pydantic request/response
└── core/               # Fonctionnalités transversales
```

## API Response Formats

**Succès :** Format direct (pas de wrapper)
```json
{ "id": "abc", "subjective": "...", "createdAt": "2026-01-17T10:30:00Z" }
```

**Erreur :** Format structuré
```json
{
  "error": {
    "code": "QUOTA_EXCEEDED",
    "message": "Vous avez atteint votre quota mensuel",
    "details": { "used": 50, "limit": 50 }
  }
}
```

**Codes d'erreur standardisés :**

| Code HTTP | Code Erreur | Usage |
|-----------|-------------|-------|
| 400 | `INVALID_REQUEST` | Requête mal formée |
| 400 | `VALIDATION_ERROR` | Données invalides |
| 401 | `UNAUTHORIZED` | Token manquant/expiré |
| 403 | `QUOTA_EXCEEDED` | Quota mensuel atteint |
| 403 | `TRIAL_EXPIRED` | Période d'essai terminée |
| 404 | `NOT_FOUND` | Ressource inexistante |
| 413 | `AUDIO_TOO_LONG` | Audio > 10 minutes |
| 429 | `RATE_LIMITED` | Trop de requêtes |
| 500 | `INTERNAL_ERROR` | Erreur serveur |
| 503 | `SERVICE_UNAVAILABLE` | Service externe down |

## Date & Data Formats

| Contexte | Format |
|----------|--------|
| **Dates API (JSON)** | ISO 8601 UTC : `2026-01-17T10:30:00Z` |
| **Dates DB** | TIMESTAMP WITH TIME ZONE |
| **Dates UI** | Localisé selon langue utilisateur |
| **JSON fields** | camelCase (conversion auto Pydantic) |

## Business Rules (Implementation Critical)

**Règle de langue des notes :**
La note SOAP générée est **TOUJOURS** dans la langue de l'application de l'utilisateur (`user.app_language`), **jamais** dans la langue de la transcription audio.

```python
# Correct : langue = setting utilisateur
note = await extract_soap_note(
    transcript=transcript,  # peut être en DE, EN, FR, ES, autre
    output_language=user.app_language  # FR, DE, ou EN selon setting user
)

# Incorrect : ne jamais détecter la langue du transcript pour output
```

**Exemple :** Un kiné suisse avec app en français enregistre un patient germanophone → la note est générée en français.

## Process Patterns

**Loading States (Frontend) :**
```tsx
if (error) return <ErrorMessage error={error} />;
if (isLoading) return <Skeleton />;
if (data.length === 0) return <EmptyState />;
return <DataList data={data} />;
```

**Error Handling :**
- Erreur réseau → Toast + retry automatique (TanStack Query)
- Erreur validation → Message inline
- Erreur quota → Modal avec CTA upgrade
- Erreur serveur → Toast + log Sentry

**Retry Pattern :**
- Frontend : TanStack Query avec 3 retries + backoff exponentiel
- Backend : tenacity avec 3 retries pour appels externes (Deepgram, Mistral)

## Logging Standards

**Niveaux :**
| Niveau | Usage |
|--------|-------|
| DEBUG | Dev uniquement, détails techniques |
| INFO | Événements normaux importants |
| WARNING | Problèmes non-bloquants |
| ERROR | Erreurs à investiguer |

**Format (Production) :** JSON structuré avec timestamp, level, message, context

## Git Conventions

**Commits :** Conventional Commits
```
feat(recording): add pause/resume functionality
fix(auth): handle expired JWT token gracefully
docs(api): add endpoint documentation
refactor(notes): extract SOAP formatting to service
test(quota): add unit tests for quota calculation
chore(deps): update TanStack Query to v5.18
```

**Branches :**
- `main` : Production, toujours déployable
- `feat/xxx` : Nouvelle feature
- `fix/xxx` : Correction de bug

## Security Rules

**Interdit :**
- ❌ Clés API dans le code → Variables d'environnement
- ❌ `console.log` de tokens/passwords → Logger uniquement les IDs
- ❌ SQL brut avec concaténation → SQLAlchemy ORM
- ❌ `.env` dans Git → `.env.example` avec placeholders

**Variables d'environnement :** SCREAMING_SNAKE_CASE avec préfixe service
```bash
DATABASE_URL=...
GOOGLE_CLIENT_ID=...
DEEPGRAM_API_KEY=...
MISTRAL_API_KEY=...
STRIPE_SECRET_KEY=...
SENTRY_DSN=...
```

## Test Conventions

**Nommage Frontend :**
```typescript
describe('RecordButton', () => {
  it('should start recording when clicked', () => {});
});
```

**Nommage Backend :**
```python
def test_create_note_returns_soap_structure():
    ...
def test_create_note_fails_when_quota_exceeded():
    ...
```

**Structure :** Arrange - Act - Assert (AAA)
