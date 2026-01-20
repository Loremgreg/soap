# Story 1.1: Project Setup & Infrastructure

Status: ready-for-dev

## Story

As a developer,
I want a fully configured project with frontend, backend, and database infrastructure,
So that I can start implementing user-facing features on a solid foundation.

## Acceptance Criteria

### AC1: Frontend Development Server
**Given** a new development environment
**When** the project is cloned and dependencies installed
**Then** the frontend dev server starts on localhost:5173 with Vite + React + TypeScript
**And** shadcn/ui is configured with base components (Button, Card, Toast, Dialog)
**And** TailwindCSS is configured with mobile-first breakpoints (320px, 768px, 1024px)
**And** TanStack Router is configured with type-safe routes

### AC2: Backend Server
**Given** the backend project structure
**When** the FastAPI server starts
**Then** it runs on localhost:8000 with async support
**And** SQLAlchemy 2.0 async is configured with Pydantic v2 schemas
**And** Alembic migrations are initialized
**And** CORS is configured for frontend origin

### AC3: Database Connection
**Given** the database configuration
**When** connecting to Neon PostgreSQL
**Then** the connection uses EU region (Frankfurt)
**And** SSL/TLS is enforced
**And** connection pooling is configured

### AC4: Deployment Configuration
**Given** the deployment configuration
**When** code is pushed to main branch
**Then** frontend auto-deploys to Vercel
**And** backend auto-deploys to Railway EU region
**And** environment variables are properly configured

## Tasks / Subtasks

### Task 1: Project Root Setup (AC: 1, 2, 3, 4)
- [ ] 1.1 Create root `.gitignore` with Node, Python, env files patterns
- [ ] 1.2 Create root `.env.example` with all required environment variables
- [ ] 1.3 Create root `README.md` with setup instructions

### Task 2: Frontend Initialization (AC: 1)
- [ ] 2.1 Initialize Vite project with React + TypeScript template
  ```bash
  npm create vite@latest frontend -- --template react-ts
  ```
- [ ] 2.2 Install and configure TailwindCSS
  ```bash
  npm install -D tailwindcss postcss autoprefixer
  npx tailwindcss init -p
  ```
- [ ] 2.3 Configure `tailwind.config.js` with mobile-first breakpoints
- [ ] 2.4 Initialize shadcn/ui and install base components
  ```bash
  npx shadcn-ui@latest init
  npx shadcn-ui@latest add button card toast dialog textarea select badge skeleton
  ```
- [ ] 2.5 Install and configure TanStack Router
  ```bash
  npm install @tanstack/react-router
  ```
- [ ] 2.6 Install TanStack Query for data fetching
  ```bash
  npm install @tanstack/react-query
  ```
- [ ] 2.7 Install Zustand for local state management
  ```bash
  npm install zustand
  ```
- [ ] 2.8 Create folder structure: `features/`, `components/`, `hooks/`, `lib/`, `types/`, `routes/`
- [ ] 2.9 Create PWA manifest (`public/manifest.json`) with app icons
- [ ] 2.10 Create `.env.example` and `.env.local` for frontend

### Task 3: Backend Initialization (AC: 2)
- [ ] 3.1 Create `backend/` folder structure
- [ ] 3.2 Create `requirements.txt` with all dependencies:
  - fastapi, uvicorn[standard]
  - sqlalchemy[asyncio], asyncpg
  - alembic
  - pydantic, pydantic-settings
  - authlib, httpx
  - python-jose[cryptography]
  - slowapi
  - sentry-sdk[fastapi]
- [ ] 3.3 Create `requirements-dev.txt`:
  - pytest, pytest-asyncio
  - httpx (for testing)
- [ ] 3.4 Create `pyproject.toml` with project metadata
- [ ] 3.5 Create `app/main.py` FastAPI entry point with:
  - CORS middleware configured for `http://localhost:5173`
  - Sentry SDK initialization
  - Health check endpoint `/health`
  - API version prefix `/api/v1`
- [ ] 3.6 Create `app/config.py` with Pydantic Settings for env vars
- [ ] 3.7 Create folder structure: `routers/`, `services/`, `models/`, `schemas/`, `core/`, `tests/`
- [ ] 3.8 Create `app/core/exceptions.py` with standardized error response format
- [ ] 3.9 Create `.env.example` for backend

### Task 4: Database Setup (AC: 3)
- [ ] 4.1 Create `app/core/database.py` with async SQLAlchemy engine
  - Connection pooling (pool_size=5, max_overflow=10)
  - SSL mode required
  - Async session factory
- [ ] 4.2 Create `app/models/base.py` with Base model class
- [ ] 4.3 Initialize Alembic:
  ```bash
  alembic init alembic
  ```
- [ ] 4.4 Configure `alembic/env.py` for async migrations
- [ ] 4.5 Update `alembic.ini` with database URL variable

### Task 5: CI/CD & Deployment Config (AC: 4)
- [ ] 5.1 Create `frontend/vercel.json` for Vercel deployment
- [ ] 5.2 Create `backend/Dockerfile` for Railway
- [ ] 5.3 Create `backend/railway.json` or `railway.toml` if needed
- [ ] 5.4 Document deployment steps in README

### Task 6: Verification & Testing (AC: 1, 2, 3)
- [ ] 6.1 Verify frontend starts: `npm run dev` on port 5173
- [ ] 6.2 Verify backend starts: `uvicorn app.main:app --reload` on port 8000
- [ ] 6.3 Verify CORS allows frontend to call backend `/health`
- [ ] 6.4 Create `backend/tests/conftest.py` with test fixtures
- [ ] 6.5 Create basic test `test_health.py` to verify server runs

## Dev Notes

### Critical Architecture Decisions (DO NOT DEVIATE)

| Decision | Implementation | Source |
|----------|---------------|--------|
| **ORM** | SQLAlchemy 2.0 async | [architecture/core-architectural-decisions.md] |
| **Migrations** | Alembic | [architecture/core-architectural-decisions.md] |
| **State Management** | Zustand (local) + TanStack Query (server) | [architecture/core-architectural-decisions.md] |
| **Routing** | TanStack Router (type-safe) | [architecture/core-architectural-decisions.md] |
| **API Versioning** | `/api/v1/` prefix | [architecture/core-architectural-decisions.md] |
| **JWT Storage** | httpOnly Cookie | [architecture/core-architectural-decisions.md] |

### Project Structure (MANDATORY)

Refer to [project-context.md] for complete structure. Key points:

**Frontend (`frontend/src/`):**
```
src/
├── features/           # Par fonctionnalite (auth/, recording/, notes/, billing/, settings/)
├── components/         # Composants partages
│   ├── ui/            # shadcn/ui components
│   └── layout/        # Header, BottomNav, PageContainer
├── hooks/             # Hooks partages
├── lib/               # Utilitaires (api.ts, utils.ts, queryClient.ts)
├── types/             # Types globaux
└── routes/            # TanStack Router routes
```

**Backend (`backend/app/`):**
```
app/
├── routers/           # Endpoints API par domaine
├── services/          # Logique metier
├── models/            # SQLAlchemy ORM
├── schemas/           # Pydantic request/response
├── core/              # database.py, security.py, exceptions.py
└── tests/             # Tests co-located
```

### Coding Standards (MANDATORY)

| Context | Convention | Example |
|---------|------------|---------|
| DB Tables/Columns | snake_case | `soap_notes`, `user_id` |
| API Endpoints | Plural + kebab-case | `/api/v1/soap-notes` |
| React Components | PascalCase | `RecordButton.tsx` |
| React Hooks | camelCase + use | `useRecording.ts` |
| Python Files | snake_case | `soap_notes.py` |
| Python Functions | snake_case | `get_user_quota()` |
| JSON API Fields | camelCase | `createdAt`, `userId` |
| Constants | SCREAMING_SNAKE_CASE | `API_BASE_URL` |

### Error Response Format (MANDATORY)

```json
{
  "error": {
    "code": "ERROR_CODE",
    "message": "Human readable message",
    "details": { }
  }
}
```

### Environment Variables Required

```bash
# Database
DATABASE_URL=postgresql+asyncpg://user:pass@host/db?sslmode=require

# Frontend
VITE_API_BASE_URL=http://localhost:8000

# Backend
APP_ENV=development
FRONTEND_URL=http://localhost:5173
JWT_SECRET_KEY=your-secret-key
SENTRY_DSN=optional-for-dev

# External Services (not needed for this story)
# GOOGLE_CLIENT_ID, GOOGLE_CLIENT_SECRET
# DEEPGRAM_API_KEY, MISTRAL_API_KEY
# STRIPE_SECRET_KEY, STRIPE_WEBHOOK_SECRET
```

### Library Versions (Use Latest Stable)

**Frontend:**
- Vite: ^5.x
- React: ^18.x
- TypeScript: ^5.x
- TailwindCSS: ^3.x
- @tanstack/react-router: ^1.x
- @tanstack/react-query: ^5.x
- zustand: ^4.x

**Backend:**
- Python: 3.11+
- FastAPI: ^0.109.x
- SQLAlchemy: ^2.0.x
- Pydantic: ^2.x
- Alembic: ^1.13.x

### Testing Requirements

- Frontend: Tests co-located with components (`Component.test.tsx`)
- Backend: Tests in `app/tests/` with pytest + pytest-asyncio
- Test naming: `test_<function>_<expected_behavior>`

### Security Checklist

- [ ] No API keys in code - all in environment variables
- [ ] `.env` files in `.gitignore`
- [ ] `.env.example` files with placeholders only
- [ ] CORS restricted to frontend origin
- [ ] SSL required for database connection

## References

- [Source: project-context.md] - Complete technical stack and patterns
- [Source: docs/planning-artifacts/architecture/project-structure-boundaries.md] - Directory structure
- [Source: docs/planning-artifacts/architecture/core-architectural-decisions.md] - Tech decisions
- [Source: docs/planning-artifacts/architecture/implementation-patterns-coding-standards.md] - Coding standards
- [Source: docs/planning-artifacts/prd/scope-produit.md] - MVP scope

## Dev Agent Record

### Agent Model Used

_To be filled by dev agent_

### Debug Log References

_To be filled during implementation_

### Completion Notes List

_To be filled after implementation_

### File List

_To be filled with all created/modified files_
