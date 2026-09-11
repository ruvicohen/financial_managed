# Financial Managed

A secure, cloud-hosted family financial management platform: a unified view
of a household's finances via a web dashboard and an LLM-powered
conversational interface. See
[`docs/family_financial_platform_master_plan.md`](docs/family_financial_platform_master_plan.md)
for the full product and technical plan.

This repository currently implements **Phase 0 - Engineering Foundation** and
**Phase 1 - Authentication & Household**: Google sign-in (allowlisted to the two
partners), DB-backed sessions, one shared household with a copy-paste invite
link for the second partner, and household-scoped authorization. No financial
features yet. See [`docs/phase0-setup.md`](docs/phase0-setup.md) and
[`docs/phase1-setup.md`](docs/phase1-setup.md) for the manual cloud-account and
Google-OAuth setup needed before a real deployment goes live.

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

At minimum, `.env` needs `APP_ENV` and `DATABASE_URL` (defaults in
`.env.example` work with the local Docker Compose Postgres below). To exercise
the login flow you also need `GOOGLE_CLIENT_ID`, `GOOGLE_CLIENT_SECRET`,
`SESSION_SECRET`, `ALLOWED_GOOGLE_EMAILS`, and `COOKIE_SECURE=false` - see
[`docs/phase1-setup.md`](docs/phase1-setup.md). The remaining variables (AI
providers, Telegram, object storage, Redis) are placeholders for later phases -
leave them blank.

### Google OAuth

Sign-in uses the Google authorization-code flow, gated by an email allowlist
(`ALLOWED_GOOGLE_EMAILS`). Create a Google Cloud OAuth *Web application* client
with redirect URI `http://localhost:8000/api/v1/auth/google/callback`; full
steps are in [`docs/phase1-setup.md`](docs/phase1-setup.md).

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

The app listens on `http://localhost:3000`. Unauthenticated visits redirect to
`/login`; after Google sign-in you land on `/dashboard` to create the household
and generate an invite link for the second partner.

## Tests

```bash
# Backend - needs the local Postgres running (docker compose up -d postgres).
# Tests migrate the DB and run inside a rolled-back transaction each.
DATABASE_URL=postgresql+psycopg://postgres:postgres@localhost:5433/financial_managed \
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
- [`docs/phase0-setup.md`](docs/phase0-setup.md) - manual cloud setup steps
  (Render blueprint activation).
- [`docs/phase1-setup.md`](docs/phase1-setup.md) - Google OAuth client setup and
  the Phase 1 environment variables.
