# Financial Managed

A secure, cloud-hosted family financial management platform: a unified view
of a household's finances via a web dashboard and an LLM-powered
conversational interface. See
[`docs/family_financial_platform_master_plan.md`](docs/family_financial_platform_master_plan.md)
for the full product and technical plan.

This repository currently implements **Phase 0 - Engineering Foundation**:
a working backend, frontend, database, and CI pipeline, with no financial
features yet. See [`docs/phase0-setup.md`](docs/phase0-setup.md) for the
manual cloud-account setup still needed before a real deployment goes live.

## Architecture

```
financial_managed/
├── apps/
│   ├── api/          FastAPI backend (Python)
│   └── web/           Next.js frontend (TypeScript)
├── workers/            Async job workers (not implemented yet)
├── packages/            Shared code across apps (not implemented yet)
├── infra/                Infrastructure-as-code (not implemented yet)
├── docs/                  Architecture and planning docs
├── docker-compose.yml      Local Postgres+pgvector (and optional full stack)
└── render.yaml               Render deployment blueprint (not activated yet)
```

Backend: FastAPI + SQLAlchemy 2.x + Alembic + PostgreSQL/pgvector, managed
with `uv`. Frontend: Next.js (App Router) + TypeScript + Tailwind CSS +
shadcn/ui, managed with `pnpm`.

## Prerequisites

| Tool       | Version    |
| ---------- | ---------- |
| Python     | 3.12.x (see `.python-version`) |
| Node.js    | 24 LTS (see `.nvmrc`) |
| pnpm       | >= 9       |
| uv         | latest     |
| Docker     | latest, with Docker Compose |

## Clone

```bash
git clone https://github.com/ruvicohen/financial_managed.git
cd financial_managed
```

## Environment setup

```bash
cp .env.example apps/api/.env
cp apps/web/.env.example apps/web/.env.local
```

(The backend reads `.env` relative to its own working directory, which is
`apps/api` when you run `uvicorn`/`alembic` below - hence copying it there
rather than to the repo root.)

At minimum, `.env` needs `APP_ENV` and `DATABASE_URL` filled in (defaults in
`.env.example` work with the local Docker Compose Postgres below). Every
other variable is a placeholder reserved for later phases (Google OAuth, AI
providers, Telegram, object storage, Redis) - leave them blank for now.

### Google OAuth (not implemented yet)

Phase 0 ships no authentication - `GOOGLE_CLIENT_ID`/`GOOGLE_CLIENT_SECRET`
are unused placeholders. See
[`docs/phase0-setup.md`](docs/phase0-setup.md#google-oauth-needed-starting-phase-1-not-phase-0)
if you want to prepare a Google Cloud OAuth client ahead of Phase 1.

## Database startup

```bash
docker compose up -d postgres
```

This starts PostgreSQL 17 with the `pgvector` extension available, exposed
on host port **5433** (not 5432, to avoid colliding with any PostgreSQL
already installed locally).

## Migrations

```bash
cd apps/api
uv sync
uv run alembic upgrade head
```

## Backend startup

```bash
cd apps/api
uv run uvicorn app.main:app --reload
```

The API listens on `http://localhost:8000`. Check `GET /health` (liveness)
and `GET /ready` (liveness + DB connectivity).

## Frontend startup

```bash
pnpm install
pnpm --filter web dev
```

The app listens on `http://localhost:3000` and displays the backend's
`/health` status, proving frontend-to-backend connectivity in development.

## Tests

```bash
# Backend
uv run pytest

# Frontend
pnpm --filter web test
```

## Lint / type-check

```bash
# Backend
uv run ruff check .
uv run ruff format --check .
uv run mypy apps/api/app apps/api/alembic apps/api/tests

# Frontend
pnpm --filter web lint
pnpm --filter web typecheck
```

## Docker

Build and run the full stack (Postgres + API + web) in containers:

```bash
docker compose up -d --build
```

Or build/run an individual image:

```bash
docker build -f apps/api/Dockerfile -t financial-managed-api .
docker build -f apps/web/Dockerfile -t financial-managed-web .
```

## Production deployment

Not activated yet. `render.yaml` at the repo root declares the target
Render Blueprint (API service, web service, managed Postgres); once a
Render account is connected to this GitHub repository, pushes to `main`
auto-deploy per that blueprint. See
[`docs/phase0-setup.md`](docs/phase0-setup.md#deploy-to-render) for the
manual account-setup steps required before that happens.

## CI

GitHub Actions (`.github/workflows/ci.yml`) runs on every pull request and
push to `main`: backend lint/type-check/tests, frontend lint/type-check/
tests/build, a migration check against a fresh Postgres, and a secret-
hygiene scan (gitleaks).

## Documentation

- [`docs/family_financial_platform_master_plan.md`](docs/family_financial_platform_master_plan.md) -
  full product and technical plan (all phases).
- [`docs/phase0-setup.md`](docs/phase0-setup.md) - manual cloud/OAuth setup
  steps not covered by this repo's code.
