# NetPulse

[![Live Demo](https://img.shields.io/badge/Demo-Vercel%20Live-black?style=flat&logo=vercel)](https://netpulse-weld.vercel.app)
[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](https://opensource.org/licenses/MIT)
[![Python 3.11+](https://img.shields.io/badge/python-3.11+-3776AB?logo=python&logoColor=white)](https://www.python.org/)
[![Vue 3](https://img.shields.io/badge/vue-3-4FC08D?logo=vuedotjs&logoColor=white)](https://vuejs.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.115-009688?logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com/)

[Deutsch](#deutsch) | [English](#english)

---

## Deutsch

### Übersicht

NetPulse ist eine simulierte ISP-Konsole. Sie erzeugt Verkehr aus einem Seed und leitet
ihn durch DNS-/Policy-Regeln, einen Cache und ein Dashboard. Demo-Projekt. Keine echten
Pakete, keine echte Firewall, kein echter DNS-Server.

**Live:** [netpulse-weld.vercel.app](https://netpulse-weld.vercel.app)

### Funktionen

- Deterministische Simulation: Seed, Dauer, Anfragerate, Cache-TTL/Kapazität/Policy
- Policy-Regeln: allow, block, rate-limit, route; priorisiertes Matching mit
  Client-/Domain-Matchern (Wildcard, Gruppe, Kategorie)
- Workspaces pro Browser-Sitzung via HttpOnly-Cookie
- Cache-Lab: LRU/FIFO/none, TTL-Ablauf, Eviction-Zähler
- Dashboard: Hit-Rate, blockierte Anfragen, Latenz, Aktionsaufschlüsselung
- Ereignis-Browser: Filter nach Aktion/Client/Domain, paginiert
- Berichte: JSON mit Assertions und Limitationen

### Tech-Stack

Backend: FastAPI (Python 3.11+), SQLAlchemy (SQLite/Postgres), Alembic, Pydantic

Frontend: Vue 3, Vite, TypeScript, i18n (DE/EN)

Infrastruktur: Docker, Docker Compose, Nginx

### Schnellstart

Voraussetzungen: Python 3.11+, Node 20+. Optional Postgres.

Backend:
```bash
cd backend
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```
Standardmäßig SQLite.

Frontend:
```bash
cd frontend
npm install
npm run dev
```
Öffnen: http://localhost:5173

Docker:
```bash
docker compose up --build
```

### Konfiguration

| Variable | Standard | Hinweis |
|---|---|---|
| `DATABASE_URL` | `sqlite:///./netpulse.db` | Postgres möglich |
| `AUTO_CREATE_TABLES` | `true` | In Produktion `false` |
| `COOKIE_SECURE` | `false` | Hinter HTTPS `true` |
| `CORS_ORIGINS` | `http://localhost:5173` | Komma-getrennt |

### API

- `GET /api/health`
- `GET /api/clients`, `GET /api/domains`
- `GET/POST/PUT/DELETE/PATCH /api/rules`
- `POST /api/simulate`
- `GET /api/runs`, `/api/runs/{id}`, `/api/runs/{id}/events`, `/api/runs/{id}/report`
- `GET /api/dashboard?run_id=`

### Tests

```bash
cd backend && pytest
cd frontend && npm run build
cd frontend && npx playwright test
```

---

## English

### Overview

NetPulse is a simulated ISP console. It generates traffic from a seed and runs it
through DNS/policy rules, a cache, and a dashboard. Demo project. No real packets,
no real firewall, no real DNS server.

**Live:** [netpulse-weld.vercel.app](https://netpulse-weld.vercel.app)

### Features

- Deterministic simulation: seed, duration, request rate, cache TTL/capacity/policy
- Policy rules: allow, block, rate-limit, route; priority matching with
  client/domain matchers (wildcard, group, category)
- Per-browser-session workspaces via HttpOnly cookie
- Cache lab: LRU/FIFO/none, TTL expiry, eviction counts
- Dashboard: hit ratio, blocked count, latency, action breakdown
- Event browser: filter by action/client/domain, paginated
- Reports: JSON with assertions and limitations

### Tech Stack

Backend: FastAPI (Python 3.11+), SQLAlchemy (SQLite/Postgres), Alembic, Pydantic

Frontend: Vue 3, Vite, TypeScript, i18n (DE/EN)

Infrastructure: Docker, Docker Compose, Nginx

### Quick Start

Prerequisites: Python 3.11+, Node 20+. Optional Postgres.

Backend:
```bash
cd backend
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```
SQLite by default.

Frontend:
```bash
cd frontend
npm install
npm run dev
```
Open: http://localhost:5173

Docker:
```bash
docker compose up --build
```

### Configuration

| Variable | Default | Notes |
|---|---|---|
| `DATABASE_URL` | `sqlite:///./netpulse.db` | Postgres supported |
| `AUTO_CREATE_TABLES` | `true` | Set `false` in production |
| `COOKIE_SECURE` | `false` | Set `true` behind HTTPS |
| `CORS_ORIGINS` | `http://localhost:5173` | Comma-separated |

### API

- `GET /api/health`
- `GET /api/clients`, `GET /api/domains`
- `GET/POST/PUT/DELETE/PATCH /api/rules`
- `POST /api/simulate`
- `GET /api/runs`, `/api/runs/{id}`, `/api/runs/{id}/events`, `/api/runs/{id}/report`
- `GET /api/dashboard?run_id=`

### Tests

```bash
cd backend && pytest
cd frontend && npm run build
cd frontend && npx playwright test
```
EOF
echo done