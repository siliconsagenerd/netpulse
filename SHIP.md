# Ship / deployment (future, not done)

This pass did not deploy. To deploy later:
1. Provision Postgres; set DATABASE_URL; run `alembic upgrade head` with
   AUTO_CREATE_TABLES=false.
2. Set COOKIE_SECURE=true and a specific CORS origin list.
3. Build frontend with VITE_API_BASE pointing at the API; deploy static build.
4. Run Playwright e2e against the deployed URLs.
5. Record real CI run before claiming CI passed.

No remote, DNS, or cloud resources were created in this remediation pass.
