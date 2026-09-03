# Phase 0 Manual Follow-Up

These steps require your own accounts/credentials and were intentionally
**not** performed as part of the Phase 0 engineering foundation. Everything
else (repo scaffold, backend, frontend, Docker images, CI, deployment
configs) is done and verified locally.

## Deploy to Render

1. Create a Render account at https://render.com if you don't have one.
2. From the Render dashboard, create a new Blueprint and connect this
   GitHub repository (`ruvicohen/financial_managed`).
3. Render should auto-detect `render.yaml` at the repo root and propose the
   `financial-managed-api`, `financial-managed-web`, and
   `financial-managed-db` resources it defines.
4. **Verify pgvector support**: confirm the Postgres plan you select
   supports the `vector` extension. If it doesn't, use an external
   Postgres provider with pgvector support instead and point `DATABASE_URL`
   at it manually (remove the `fromDatabase` binding in `render.yaml`).
5. In the Render dashboard, set the secret environment variables marked
   `sync: false` in `render.yaml` (Google OAuth credentials, LLM/embedding
   API keys, Telegram bot token, object storage credentials, Redis URL) -
   only fill in the ones needed by features you've actually implemented;
   the rest can stay empty until later phases.
6. Deploy. Confirm the public HTTPS URL Render assigns is reachable and
   `/health` on the API service returns `{"status": "ok"}`.
7. (Optional) Configure a custom domain in Render's dashboard.

## Google OAuth (needed starting Phase 1, not Phase 0)

No code consumes these yet - Phase 0 ships no authentication. To prepare
ahead of Phase 1:

1. Create a project in the [Google Cloud Console](https://console.cloud.google.com/).
2. Configure the OAuth consent screen.
3. Create OAuth 2.0 credentials (Web application type).
4. Add authorized redirect URIs for both local development
   (`http://localhost:8000/...`) and the production URL once known.
5. Set `GOOGLE_CLIENT_ID` / `GOOGLE_CLIENT_SECRET` in your local `.env` and
   in Render's environment variables when Phase 1 lands.

## GitHub branch protection (optional, recommended once CI is live)

Once `ci.yml` has run successfully on `main` at least once, consider
enabling in GitHub repo settings:

- Require pull requests before merging
- Require the `backend-quality`, `frontend-quality`, `migration-validation`,
  and `secret-hygiene` status checks to pass before merging
- Prevent force pushes and branch deletion on `main`
