# SOAP Notice

Application de transcription audio pour physiothérapeutes - transforme des enregistrements d'anamnèses en notes SOAP structurées.

## Stack Technique

| Composant | Technologie |
|-----------|-------------|
| **Frontend** | Vite + React + TypeScript + TailwindCSS + shadcn/ui |
| **State** | Zustand (local) + TanStack Query (serveur) |
| **Routing** | TanStack Router |
| **Backend** | Python FastAPI (async) |
| **ORM** | SQLAlchemy 2.0 async |
| **Database** | Neon PostgreSQL (EU) |
| **STT** | Deepgram API (nova-3) |
| **LLM** | Mistral AI |
| **Payments** | Stripe |

## Prérequis

- Node.js 18+
- Python 3.11+
- PostgreSQL (ou compte Neon)

## Installation

### 1. Cloner le projet

```bash
git clone <repo-url>
cd soap-notice
```

### 2. Configuration

```bash
cp .env.example .env
# Éditer .env avec vos valeurs
```

### 3. Frontend

```bash
cd frontend
npm install
npm run dev
# → http://localhost:5173
```

### 4. Backend

```bash
cd backend
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
pip install -r requirements-dev.txt

# Migrations
alembic upgrade head

# Démarrer le serveur
uvicorn app.main:app --reload
# → http://localhost:8000
```

## Structure Projet

```
soap-notice/
├── frontend/                # React + Vite
│   ├── src/
│   │   ├── features/       # Par fonctionnalité
│   │   ├── components/     # Composants partagés
│   │   ├── hooks/          # Hooks partagés
│   │   ├── lib/            # Utilitaires
│   │   ├── types/          # Types TypeScript
│   │   └── routes/         # TanStack Router
│   └── public/
├── backend/                 # Python FastAPI
│   ├── app/
│   │   ├── routers/        # Endpoints API
│   │   ├── services/       # Logique métier
│   │   ├── models/         # SQLAlchemy ORM
│   │   ├── schemas/        # Pydantic
│   │   ├── core/           # Config, DB, exceptions
│   │   └── tests/          # Tests pytest
│   └── alembic/            # Migrations
└── docs/                    # Documentation
```

## API

- Base URL: `http://localhost:8000/api/v1`
- Health Check: `GET /health`
- Documentation: `http://localhost:8000/docs`

## Tests

```bash
# Backend
cd backend
pytest

# Frontend
cd frontend
npm test
```

## Déploiement

- **Frontend**: Vercel (auto-deploy depuis main)
- **Backend**: Railway EU region
- **Database**: Neon PostgreSQL Frankfurt

## Langues Supportées

- Français
- Allemand
- Anglais

## Licence

Propriétaire - Tous droits réservés
