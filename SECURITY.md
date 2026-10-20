# Security notes (local prototype)

- Anonymous per-browser workspaces via server-issued opaque token in an HttpOnly
  cookie; only the token hash is stored server-side.
- Secure cookie flag follows COOKIE_SECURE env (false locally, true in HTTPS prod).
- SameSite=Lax; same-origin API access by default.
- Mutable rules/runs/events/dashboard scoped to the validated workspace.
- Shared reference clients/domains are read-only.
- Caller-supplied workspace identifiers are not accepted as access selectors.
- Limits: max 5000 events/run, 50 retained runs/workspace, 2 concurrent runs/workspace,
  10000 global runs.
- No arbitrary external DNS/HTTP fetching, shell execution, or user code.
- No paid AI features.

Not production-hardened: no authentication, no rate limiting at the edge, no TLS
termination in repo. Local prototype only.
