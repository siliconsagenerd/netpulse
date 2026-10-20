# Runbook (local + production)

## Start (local)
Backend: `cd backend && uvicorn app.main:app --reload --port 8000`
Frontend: `cd frontend && npm run dev` (http://localhost:5173)

## Migrate
`cd backend && alembic upgrade head` (idempotent).
Repository head revision: `52484d6f06f5`. Verify with `alembic heads`.

## Test
`cd backend && pytest` ; `cd frontend && npm run build` ; `cd frontend && npx playwright test`

## Reset local DB (dev only)
Delete netpulse.db or drop/recreate the Postgres database, then `alembic upgrade head`.

## Limits / troubleshooting
- Max 5000 events/run, 50 runs/workspace, 2 concurrent runs/workspace.
- Stale "running" runs are failed after 5 minutes on next request.
- If cookies are blocked, API returns 401; check SameSite/origin settings.

## Deployment (clean committed source only)
1. Working tree must be clean: `git status --short` returns nothing.
2. Run CI (push triggers `.github/workflows/ci.yml`); both `backend` and `frontend` jobs must pass.
3. Deploy: `vercel --prod --yes` from the repository root.
4. Record the resulting deployment id and confirm production serves the new commit.
5. Smoke: `GET /api/health` returns `{"status":"ok","db":"ok"}`.

Do not deploy from a dirty working tree. Do not substitute an uncommitted implementation.

## Rollback (application)
Command supported by the installed Vercel CLI (v64.x):
`vercel rollback <deploymentId>` (or `vercel rollback <deployment-url>`)
Add `-y` to skip the confirmation prompt.

Last known-good deployment (pre-release): `dpl_6pvPaHBERzwfF3TSTZtkwxSFRvWz`
  (production URL https://netpulse-weld.vercel.app, commit 8b20306, deployed via CLI).
Current release deployment: `dpl_ExAKk93f8gCxbrx8yQBgz9XjHDe3`
  (production URL https://netpulse-weld.vercel.app, commit 8b20306).

## Database downgrade
Do NOT run `alembic downgrade -1` as a blanket rollback. A database downgrade requires:
- review of the specific migration's `downgrade()` and its data-loss consequences,
- a verified recovery option (backup/restore or forward-fix) tested beforehand,
- confirmation that no production data depends on the new schema.

Backups/retention are not verified in this project; do not assume they exist.
