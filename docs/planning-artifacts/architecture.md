---
stepsCompleted: [1, 2, 3, 4, 5, 6]
inputDocuments:
  - docs/planning-artifacts/prd.md
  - docs/planning-artifacts/product-brief-soap-notice-2026-01-14.md
  - docs/planning-artifacts/ux-design-specification.md
  - project-context.md
workflowType: 'architecture'
project_name: 'SOAP Notice'
user_name: 'Greg'
date: '2026-01-17'
---

# Architecture Decision Document

_This document builds collaboratively through step-by-step discovery. Sections are appended as we work through each architectural decision together._

## Project Context Analysis

### Requirements Overview

**Functional Requirements:**
L'application SOAP Notice présente un flux linéaire mais techniquement exigeant :
1. **Authentification** : OAuth Google (session management simple)
2. **Recording** : Capture audio jusqu'à 10 minutes avec Wake Lock API
3. **Transcription temps réel** : WebSocket streaming vers Deepgram nova-3
4. **Extraction SOAP** : Appel Mistral AI post-transcription (< 30s)
5. **Édition/Copie** : Interface mobile-first avec auto-save
6. **Historique limité** : Max 10 notes avec suppression rolling
7. **Gestion quotas** : Compteur temps réel avec upsell intégré
8. **Paiement** : Stripe avec anniversary billing

**Non-Functional Requirements:**
- **Performance** : Latence totale < 30s après Stop (critique)
- **Disponibilité** : 99% uptime cible
- **Sécurité** : RGPD Art. 9 compliance, TLS 1.3, chiffrement repos
- **Rétention** : Audio = 0 jours, Notes = max 10 rolling
- **Localisation données** : 100% EU (providers, hébergement, DB)

**Scale & Complexity:**
- Domaine principal : Full-stack PWA mobile-first
- Niveau de complexité : Moyen-Haut
- Composants architecturaux estimés : 8-10 modules

### Technical Constraints & Dependencies

| Contrainte | Détail |
|------------|--------|
| **LLM Provider** | Mistral AI (MVP) avec abstraction switchable vers Azure OpenAI |
| **STT Provider** | Deepgram nova-3, WebSocket streaming obligatoire |
| **Database** | PostgreSQL EU (Neon recommandé - serverless, scale-to-zero, migration facile) |
| **Backend** | Python FastAPI (async, WebSocket natif) |
| **Frontend** | Vite + React + TailwindCSS + shadcn/ui |
| **Paiement** | Stripe (webhooks, anniversary billing) |
| **Auth** | Google OAuth 2.0 |

### Database Provider Decision

**Choix : Neon (PostgreSQL Serverless)**

Justification :
- **Scale-to-zero** : Coût proche de 0€ pendant développement/faible usage
- **PostgreSQL standard** : Aucun vendor lock-in, migration triviale vers self-hosted
- **EU Data Residency** : Région Frankfurt disponible (RGPD compliant)
- **Connection pooling intégré** : Compatible FastAPI async
- **Branching** : Clone DB en 1 seconde pour tests/staging

Migration future vers self-hosted si nécessaire :
- `pg_dump` pour export complet
- Changement de `DATABASE_URL` dans `.env`
- Temps estimé : 30-60 minutes

### Cross-Cutting Concerns Identified

1. **Sécurité & Conformité RGPD** - Chiffrement, DPA providers, audit trail
2. **Gestion d'erreurs robuste** - Retry logic, fallbacks, user feedback
3. **Observabilité** - Sentry, métriques latence, monitoring quotas
4. **Internationalisation** - UI (FR/DE/EN), scripts consentement, notes multilingues
5. **État temps réel** - WebSocket status, quota counter, recording state

## Starter Template Evaluation

### Primary Technology Domain

**Full-stack PWA mobile-first** avec séparation frontend/backend :
- Frontend : Single Page Application (SPA) React
- Backend : API REST + WebSocket Python

### Starter Options Evaluated

| Composant | Options Considérées | Choix Final |
|-----------|---------------------|-------------|
| **Frontend** | Setup officiel shadcn/ui vs Template doinel1a | Setup officiel |
| **Backend** | Setup manuel vs Full Stack FastAPI Template | Setup manuel |

### Selected Starters

#### Frontend : Setup Officiel shadcn/ui

**Rationale :**
- Documentation officielle toujours à jour
- Contrôle total sur la configuration
- Pas de dépendances superflues
- Courbe d'apprentissage minimale

**Initialization Commands :**

```bash
# Créer le projet Vite + React + TypeScript
npm create vite@latest frontend -- --template react-ts
cd frontend

# Installer TailwindCSS
npm install tailwindcss @tailwindcss/vite

# Initialiser shadcn/ui
npx shadcn@latest init

# Ajouter composants MVP
npx shadcn@latest add button card textarea dialog toast select badge skeleton
```

**Architectural Decisions Provided :**
- **Language** : TypeScript strict mode
- **Styling** : TailwindCSS utility-first
- **Components** : shadcn/ui (Radix UI primitives)
- **Build** : Vite + SWC
- **Path aliases** : `@/` → `./src/`

#### Backend : Setup Manuel FastAPI

**Rationale :**
- Structure adaptée aux besoins spécifiques (WebSocket Deepgram, Mistral)
- Pas de bloat (Celery, Redis, etc. non nécessaires pour MVP)
- Facile à comprendre et maintenir
- Best practices FastAPI intégrées

**Initialization Commands :**

```bash
# Créer le projet
mkdir backend && cd backend
python -m venv venv
source venv/bin/activate

# Dépendances core
pip install fastapi "uvicorn[standard]" sqlalchemy asyncpg python-dotenv pydantic-settings

# Dépendances métier
pip install deepgram-sdk mistralai stripe authlib httpx

# Dev dependencies
pip install pytest pytest-asyncio black ruff
```

**Project Structure :**

```
backend/
├── app/
│   ├── __init__.py
│   ├── main.py              # FastAPI app entry point
│   ├── config.py            # Pydantic Settings
│   ├── routers/
│   │   ├── auth.py          # Google OAuth endpoints
│   │   ├── recording.py     # WebSocket audio streaming
│   │   ├── notes.py         # CRUD notes SOAP
│   │   └── billing.py       # Stripe webhooks
│   ├── services/
│   │   ├── deepgram.py      # STT WebSocket client
│   │   ├── mistral.py       # LLM extraction (switchable)
│   │   └── stripe.py        # Payment management
│   ├── models/              # SQLAlchemy ORM models
│   └── schemas/             # Pydantic request/response schemas
├── requirements.txt
├── .env.example
└── Dockerfile
```

**Architectural Decisions Provided :**
- **Language** : Python 3.11+
- **Framework** : FastAPI async-first
- **ORM** : SQLAlchemy 2.0 async
- **Validation** : Pydantic v2
- **Server** : Uvicorn (dev) / Gunicorn + Uvicorn workers (prod)

## Core Architectural Decisions

### Data Architecture

| Décision | Choix | Justification |
|----------|-------|---------------|
| **ORM** | SQLAlchemy 2.0 async | Standard Python, type-safe, async natif |
| **Migrations** | Alembic | Auto-génère migrations depuis modèles, rollback facile |
| **Cache** | Pas de cache MVP | < 100 users, complexité non justifiée |

### Authentication & Security

| Décision | Choix | Justification |
|----------|-------|---------------|
| **Session** | JWT | Stateless, scalable, standard API |
| **Librairie OAuth** | Authlib | Standard Python, bien documenté |
| **Stockage token** | Cookie httpOnly | Protégé XSS, envoi automatique |

### API & Communication

| Décision | Choix | Justification |
|----------|-------|---------------|
| **Versioning** | `/api/v1/` préfixe URL | Évolutivité sans breaking changes |
| **Format erreurs** | JSON structuré + codes HTTP | Standard, facile à parser côté frontend |
| **Rate limiting** | slowapi | Protection abus, simple à intégrer FastAPI |
| **WebSocket audio** | Backend proxy vers Deepgram | Sécurité (clé API cachée), contrôle quotas |

**Format d'erreur standardisé :**
```json
{
  "error": {
    "code": "QUOTA_EXCEEDED",
    "message": "Quota mensuel atteint",
    "details": { "current": 50, "limit": 50 }
  }
}
```

### Frontend Architecture

| Décision | Choix | Justification |
|----------|-------|---------------|
| **State Management** | Zustand + TanStack Query | Zustand = état local léger, TanStack Query = données serveur avec cache |
| **Routing** | TanStack Router | Cohérence avec TanStack Query, type-safe |
| **Formulaires** | React Hook Form | Performant (pas de re-render), validation intégrée |
| **Capture Audio** | Web Audio API native | 0 dépendance, suffisant pour streaming |

### Infrastructure & Deployment

| Décision | Choix | Justification |
|----------|-------|---------------|
| **Hébergement Frontend** | Vercel | Gratuit, CDN global, auto-deploy GitHub |
| **Hébergement Backend** | Railway | ~5€/mois, région EU, supporte WebSocket |
| **CI/CD** | Intégré Vercel/Railway | Push GitHub → Deploy automatique |
| **Environnements** | Variables d'env Vercel/Railway | Séparation dev/prod, secrets sécurisés |
| **Monitoring** | Sentry | Gratuit, alertes erreurs, stack traces |

### Cost Analysis MVP

| Service | Coût/mois |
|---------|-----------|
| Vercel (Frontend) | 0€ |
| Railway (Backend) | ~5€ |
| Neon (Database) | 0€ |
| Sentry (Monitoring) | 0€ |
| **Total** | **~5€/mois** |

## Implementation Patterns & Coding Standards

### Documentation Requirements

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

### Naming Conventions

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

### Project Structure

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

### API Response Formats

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

### Date & Data Formats

| Contexte | Format |
|----------|--------|
| **Dates API (JSON)** | ISO 8601 UTC : `2026-01-17T10:30:00Z` |
| **Dates DB** | TIMESTAMP WITH TIME ZONE |
| **Dates UI** | Localisé selon langue utilisateur |
| **JSON fields** | camelCase (conversion auto Pydantic) |

### Process Patterns

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

### Logging Standards

**Niveaux :**
| Niveau | Usage |
|--------|-------|
| DEBUG | Dev uniquement, détails techniques |
| INFO | Événements normaux importants |
| WARNING | Problèmes non-bloquants |
| ERROR | Erreurs à investiguer |

**Format (Production) :** JSON structuré avec timestamp, level, message, context

### Git Conventions

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

### Security Rules

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

### Test Conventions

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

## Project Structure & Boundaries

### Complete Project Directory Structure

```
soap-notice/
├── README.md
├── .gitignore
├── .env.example
│
├── frontend/                          # ══════════ FRONTEND ══════════
│   ├── package.json
│   ├── package-lock.json
│   ├── vite.config.ts
│   ├── tsconfig.json
│   ├── tsconfig.node.json
│   ├── tailwind.config.js
│   ├── postcss.config.js
│   ├── components.json                # Config shadcn/ui
│   ├── index.html
│   ├── .env.example
│   ├── .env.local                     # (gitignored)
│   │
│   ├── public/
│   │   ├── favicon.ico
│   │   ├── manifest.json              # PWA manifest
│   │   └── icons/
│   │       ├── icon-192.png
│   │       └── icon-512.png
│   │
│   └── src/
│       ├── main.tsx                   # Entry point
│       ├── App.tsx                    # Root component + Router
│       ├── index.css                  # Tailwind imports
│       │
│       ├── components/                # Composants partagés
│       │   ├── ui/                    # shadcn/ui components
│       │   │   ├── button.tsx
│       │   │   ├── card.tsx
│       │   │   ├── dialog.tsx
│       │   │   ├── textarea.tsx
│       │   │   ├── toast.tsx
│       │   │   ├── select.tsx
│       │   │   ├── badge.tsx
│       │   │   └── skeleton.tsx
│       │   └── layout/
│       │       ├── Header.tsx
│       │       ├── BottomNav.tsx
│       │       └── PageContainer.tsx
│       │
│       ├── features/                  # Features par domaine
│       │   ├── auth/                  # Authentification
│       │   │   ├── components/
│       │   │   ├── hooks/
│       │   │   ├── pages/
│       │   │   └── index.ts
│       │   ├── recording/             # Enregistrement audio
│       │   │   ├── components/
│       │   │   ├── hooks/
│       │   │   ├── pages/
│       │   │   └── index.ts
│       │   ├── notes/                 # Notes SOAP
│       │   │   ├── components/
│       │   │   ├── hooks/
│       │   │   ├── pages/
│       │   │   └── index.ts
│       │   ├── billing/               # Paiement & Quota
│       │   │   ├── components/
│       │   │   ├── hooks/
│       │   │   ├── pages/
│       │   │   └── index.ts
│       │   └── settings/              # Paramètres
│       │       ├── components/
│       │       ├── pages/
│       │       └── index.ts
│       │
│       ├── hooks/                     # Hooks partagés
│       │   ├── useApiError.ts
│       │   └── useLocalStorage.ts
│       │
│       ├── lib/                       # Utilitaires
│       │   ├── api.ts
│       │   ├── utils.ts
│       │   ├── constants.ts
│       │   └── queryClient.ts
│       │
│       ├── types/                     # Types globaux
│       │   ├── index.ts
│       │   ├── soap-note.ts
│       │   ├── user.ts
│       │   └── api.ts
│       │
│       └── routes/                    # TanStack Router
│           ├── __root.tsx
│           ├── index.tsx
│           ├── login.tsx
│           ├── history.tsx
│           ├── note.$id.tsx
│           ├── settings.tsx
│           └── billing.tsx
│
└── backend/                           # ══════════ BACKEND ══════════
    ├── requirements.txt
    ├── requirements-dev.txt
    ├── Dockerfile
    ├── .env.example
    ├── alembic.ini
    ├── pyproject.toml
    │
    ├── alembic/                       # Migrations DB
    │   ├── env.py
    │   ├── script.py.mako
    │   └── versions/
    │
    └── app/
        ├── __init__.py
        ├── main.py                    # FastAPI entry point
        ├── config.py                  # Pydantic Settings
        │
        ├── routers/                   # API Endpoints
        │   ├── __init__.py
        │   ├── auth.py                # /api/v1/auth/*
        │   ├── notes.py               # /api/v1/soap-notes/*
        │   ├── users.py               # /api/v1/users/*
        │   ├── billing.py             # /api/v1/billing/*
        │   └── recording.py           # WebSocket
        │
        ├── services/                  # Logique métier
        │   ├── __init__.py
        │   ├── deepgram.py
        │   ├── llm.py
        │   ├── mistral.py
        │   ├── stripe_service.py
        │   └── quota.py
        │
        ├── models/                    # SQLAlchemy ORM
        │   ├── __init__.py
        │   ├── base.py
        │   ├── user.py
        │   ├── note.py
        │   └── subscription.py
        │
        ├── schemas/                   # Pydantic Schemas
        │   ├── __init__.py
        │   ├── user.py
        │   ├── note.py
        │   ├── auth.py
        │   └── billing.py
        │
        ├── core/                      # Fonctionnalités transversales
        │   ├── __init__.py
        │   ├── database.py
        │   ├── security.py
        │   ├── exceptions.py
        │   ├── dependencies.py
        │   └── logging.py
        │
        └── tests/                     # Tests Backend
            ├── __init__.py
            ├── conftest.py
            ├── test_auth.py
            ├── test_notes.py
            ├── test_quota.py
            └── test_recording.py
```

### Feature to Structure Mapping

| Feature | Frontend | Backend | DB Tables |
|---------|----------|---------|-----------|
| **Auth** | `features/auth/` | `routers/auth.py`, `core/security.py` | `users` |
| **Recording** | `features/recording/` | `routers/recording.py`, `services/deepgram.py` | - |
| **Notes SOAP** | `features/notes/` | `routers/notes.py`, `services/llm.py` | `soap_notes` |
| **Billing** | `features/billing/` | `routers/billing.py`, `services/stripe_service.py` | `subscriptions` |
| **Settings** | `features/settings/` | `routers/users.py` | `users` |

### Architectural Boundaries

**API Boundaries:**
- Frontend → Backend : HTTPS REST + WebSocket
- Backend → Deepgram : WebSocket streaming
- Backend → Mistral : HTTPS REST
- Backend → Stripe : HTTPS REST + Webhooks
- Backend → Neon : PostgreSQL connection pool

**Data Flow:**
```
User Audio → Frontend (Web Audio API)
          → Backend WebSocket (/api/v1/ws/record)
          → Deepgram (STT streaming)
          → Transcript accumulated
          → Mistral AI (SOAP extraction)
          → Response to Frontend
          → Display + Edit + Copy
```

### External Services Integration

| Service | Integration Point | Auth Method |
|---------|-------------------|-------------|
| **Google OAuth** | `routers/auth.py` | OAuth 2.0 |
| **Deepgram** | `services/deepgram.py` | API Key (header) |
| **Mistral AI** | `services/mistral.py` | API Key (header) |
| **Stripe** | `services/stripe_service.py` | Secret Key + Webhook Secret |
| **Sentry** | `main.tsx` + `main.py` | DSN |
| **Neon** | `core/database.py` | Connection string |

