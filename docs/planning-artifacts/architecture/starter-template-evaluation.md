# Starter Template Evaluation

## Primary Technology Domain

**Full-stack PWA mobile-first** avec séparation frontend/backend :
- Frontend : Single Page Application (SPA) React
- Backend : API REST + WebSocket Python

## Starter Options Evaluated

| Composant | Options Considérées | Choix Final |
|-----------|---------------------|-------------|
| **Frontend** | Setup officiel shadcn/ui vs Template doinel1a | Setup officiel |
| **Backend** | Setup manuel vs Full Stack FastAPI Template | Setup manuel |

## Selected Starters

### Frontend : Setup Officiel shadcn/ui

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

### Backend : Setup Manuel FastAPI

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
