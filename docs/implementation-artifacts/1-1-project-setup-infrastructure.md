# Story 1.1: Project Setup & Infrastructure

Status: done

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
- [x] 1.1 Create root `.gitignore` with Node, Python, env files patterns
- [x] 1.2 Create root `.env.example` with all required environment variables
- [x] 1.3 Create root `README.md` with setup instructions

### Task 2: Frontend Initialization (AC: 1)
- [x] 2.1 Initialize Vite project with React + TypeScript template
- [x] 2.2 Install and configure TailwindCSS
- [x] 2.3 Configure `tailwind.config.js` with mobile-first breakpoints
- [x] 2.4 Initialize shadcn/ui and install base components
- [x] 2.5 Install and configure TanStack Router
- [x] 2.6 Install TanStack Query for data fetching
- [x] 2.7 Install Zustand for local state management
- [x] 2.8 Create folder structure: `features/`, `components/`, `hooks/`, `lib/`, `types/`, `routes/`
- [x] 2.9 Create PWA manifest (`public/manifest.json`) with app icons
- [x] 2.10 Create `.env.example` and `.env.local` for frontend

### Task 3: Backend Initialization (AC: 2)
- [x] 3.1 Create `backend/` folder structure
- [x] 3.2 Create `requirements.txt` with all dependencies
- [x] 3.3 Create `requirements-dev.txt`
- [x] 3.4 Create `pyproject.toml` with project metadata
- [x] 3.5 Create `app/main.py` FastAPI entry point with CORS, Sentry, health endpoints
- [x] 3.6 Create `app/config.py` with Pydantic Settings for env vars
- [x] 3.7 Create folder structure: `routers/`, `services/`, `models/`, `schemas/`, `core/`, `tests/`
- [x] 3.8 Create `app/core/exceptions.py` with standardized error response format
- [x] 3.9 Create `.env.example` for backend

### Task 4: Database Setup (AC: 3)
- [x] 4.1 Create `app/core/database.py` with async SQLAlchemy engine (pool_size=5, max_overflow=10, SSL required)
- [x] 4.2 Create `app/models/base.py` with Base model class and TimestampMixin
- [x] 4.3 Initialize Alembic
- [x] 4.4 Configure `alembic/env.py` for async migrations
- [x] 4.5 Update `alembic.ini` with database URL variable

### Task 5: CI/CD & Deployment Config (AC: 4)
- [x] 5.1 Create `frontend/vercel.json` for Vercel deployment
- [x] 5.2 Create `backend/Dockerfile` for Railway
- [x] 5.3 Create `backend/railway.toml`
- [x] 5.4 Document deployment steps in README

### Task 6: Verification & Testing (AC: 1, 2, 3)
- [x] 6.1 Verify frontend starts: `npm run dev` on port 5173
- [x] 6.2 Verify backend starts: `uvicorn app.main:app --reload` on port 8000
- [x] 6.3 Verify CORS allows frontend to call backend `/health`
- [x] 6.4 Create `backend/tests/conftest.py` with test fixtures
- [x] 6.5 Create basic test `test_health.py` to verify server runs

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

- [x] No API keys in code - all in environment variables
- [x] `.env` files in `.gitignore`
- [x] `.env.example` files with placeholders only
- [x] CORS restricted to frontend origin
- [x] SSL required for database connection

## References

- [Source: project-context.md] - Complete technical stack and patterns
- [Source: docs/planning-artifacts/architecture/project-structure-boundaries.md] - Directory structure
- [Source: docs/planning-artifacts/architecture/core-architectural-decisions.md] - Tech decisions
- [Source: docs/planning-artifacts/architecture/implementation-patterns-coding-standards.md] - Coding standards
- [Source: docs/planning-artifacts/prd/scope-produit.md] - MVP scope

## Dev Agent Record

### Agent Model Used

Claude Opus 4.5 (claude-opus-4-5-20251101)

### Debug Log References

- Frontend build successful: 171 modules, dist generated in 1.13s
- Backend tests: 2/2 passed (test_health_check, test_api_health_check)
- CORS verification: access-control-allow-origin: http://localhost:5173

### Completion Notes List

- **Task 1**: Root setup complete - .gitignore extended, .env.example created with all variables, README.md with full documentation
- **Task 2**: Frontend initialized with Vite 7.x, React 18.x, TypeScript, TailwindCSS 3.x with mobile-first breakpoints, shadcn/ui components (Button, Card, Toast, Dialog, Textarea, Select, Badge, Skeleton), TanStack Router with type-safe routes, TanStack Query, Zustand
- **Task 3**: Backend initialized with FastAPI, CORS configured for localhost:5173, Sentry SDK setup, health endpoints (/health, /api/v1/health), standardized error format in exceptions.py
- **Task 4**: Database configured with async SQLAlchemy (pool_size=5, max_overflow=10), Base model with TimestampMixin, Alembic initialized with async migrations support
- **Task 5**: Deployment configured with vercel.json (rewrites, security headers), Dockerfile (multi-stage, non-root user, healthcheck), railway.toml
- **Task 6**: All verifications passed - frontend serves on :5173, backend on :8000, CORS working, 2 tests passing

### File List

**Created:**
- .env.example
- README.md
- frontend/ (Vite project)
  - frontend/components.json
  - frontend/tailwind.config.js
  - frontend/postcss.config.js
  - frontend/vercel.json
  - frontend/.env.example
  - frontend/.env.local
  - frontend/public/manifest.json
  - frontend/public/icons/icon-192x192.svg
  - frontend/public/icons/icon-512x512.svg
  - frontend/src/index.css
  - frontend/src/main.tsx
  - frontend/src/routeTree.gen.ts
  - frontend/src/lib/utils.ts
  - frontend/src/lib/api.ts
  - frontend/src/lib/queryClient.ts
  - frontend/src/hooks/use-toast.ts
  - frontend/src/routes/__root.tsx
  - frontend/src/routes/index.tsx
  - frontend/src/components/ui/button.tsx
  - frontend/src/components/ui/card.tsx
  - frontend/src/components/ui/toast.tsx
  - frontend/src/components/ui/toaster.tsx
  - frontend/src/components/ui/dialog.tsx
  - frontend/src/components/ui/textarea.tsx
  - frontend/src/components/ui/select.tsx
  - frontend/src/components/ui/badge.tsx
  - frontend/src/components/ui/skeleton.tsx
  - frontend/src/components/ui/index.ts
- backend/
  - backend/requirements.txt
  - backend/requirements-dev.txt
  - backend/pyproject.toml
  - backend/Dockerfile
  - backend/railway.toml
  - backend/.dockerignore
  - backend/.env.example
  - backend/app/__init__.py
  - backend/app/main.py
  - backend/app/config.py
  - backend/app/core/__init__.py
  - backend/app/core/database.py
  - backend/app/core/exceptions.py
  - backend/app/models/__init__.py
  - backend/app/models/base.py
  - backend/app/routers/__init__.py
  - backend/app/services/__init__.py
  - backend/app/schemas/__init__.py
  - backend/app/tests/__init__.py
  - backend/app/tests/conftest.py
  - backend/app/tests/test_health.py
  - backend/alembic/
  - backend/alembic/env.py
  - backend/alembic.ini

**Modified:**
- .gitignore (extended with frontend/backend patterns)
- frontend/index.html (PWA meta tags)
- frontend/tsconfig.app.json (path aliases)
- frontend/vite.config.ts (path aliases, port config)

## Change Log

| Date | Change | Author |
|------|--------|--------|
| 2026-01-20 | Story implementation complete - all tasks done, tests passing | Dev Agent (Claude Opus 4.5) |
| 2026-01-21 | Code review fixes: added PWA icons (SVG), completed Toast system (toaster.tsx + use-toast.ts), documented Railway EU region requirement, fixed conftest.py type hint | Code Review (Claude Opus 4.5) |
