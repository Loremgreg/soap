# Project Structure & Boundaries

## Complete Project Directory Structure

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

## Feature to Structure Mapping

| Feature | Frontend | Backend | DB Tables |
|---------|----------|---------|-----------|
| **Auth** | `features/auth/` | `routers/auth.py`, `core/security.py` | `users` |
| **Recording** | `features/recording/` | `routers/recording.py`, `services/deepgram.py` | - |
| **Notes SOAP** | `features/notes/` | `routers/notes.py`, `services/llm.py` | `soap_notes` |
| **Billing** | `features/billing/` | `routers/billing.py`, `services/stripe_service.py` | `subscriptions` |
| **Settings** | `features/settings/` | `routers/users.py` | `users` |

## Architectural Boundaries

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

## External Services Integration

| Service | Integration Point | Auth Method |
|---------|-------------------|-------------|
| **Google OAuth** | `routers/auth.py` | OAuth 2.0 |
| **Deepgram** | `services/deepgram.py` | API Key (header) |
| **Mistral AI** | `services/mistral.py` | API Key (header) |
| **Stripe** | `services/stripe_service.py` | Secret Key + Webhook Secret |
| **Sentry** | `main.tsx` + `main.py` | DSN |
| **Neon** | `core/database.py` | Connection string |
