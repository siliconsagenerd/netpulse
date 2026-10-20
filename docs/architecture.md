# Architecture (NetPulse)

- Backend: FastAPI (app/main.py), SQLAlchemy models (app/models/), Pydantic schemas
  (app/schemas/), routes (app/api/routes.py), simulation engine (app/simulation/engine.py).
- DB: Alembic migrations (alembic/versions/). Default SQLite; Postgres supported.
- Sessions: app/core/session.py (token + hash), app/core/deps.py (workspace resolution).
- Frontend: Vue 3 + Vite + TS; views in frontend/src/views; i18n de/en.
- Simulation is deterministic from a seed; no real networking.

## Data flow
Browser -> /api (same-origin, cookie session) -> FastAPI -> SQLAlchemy -> DB.
Workspace scoping enforced on every mutable resource and aggregate.
