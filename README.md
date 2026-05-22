# Trading Operations Dashboard

Public portfolio repository for a sanitized Vue 3 + TypeScript operational dashboard inspired by fintech and trading operations workflows.

This project uses simulated data only. It does not include real account data, credentials, private strategy logic, real server URLs, external trading integrations, or transaction placement capabilities.

## Business Problem

Operations teams need a clear view of account health, portfolio exposure, profile settings, platform status, and review logs during a busy market session. This demo shows how that kind of internal tool can be presented safely as a public portfolio project while keeping the core product thinking visible.

## Frontend Highlights

- Multi-account dashboard with status, exposure, cash, P&L, and review tickets
- Portfolio holdings table with sorting, filtering, account filters, and profile filters
- Grouped holdings rollup by symbol
- Strategy configuration modal for A/B profile settings
- Optimistic UI update example when moving holdings between profiles
- LocalStorage cache example for dashboard state and a demo-only admin key
- Mock real-time operations log viewer
- Multi-server status cards for local mock services
- Empty, loading, and error states
- Clean internal-tool layout with tables, cards, filters, and modal controls

## Tech Stack

- Vue 3
- TypeScript
- Vite
- Pinia
- Vue Router
- Local mock REST-style service in the frontend
- Optional Python/Flask mock backend for API-shape demonstration

## Architecture

```text
trading-operations-dashboard/
  src/
    api.ts                 # Local mock service and LocalStorage cache helpers
    data.ts                # Sanitized demo data and TypeScript models
    main.ts                # Vue, Pinia, and Router setup
    router/index.ts        # Vue Router configuration
    stores/dashboard.ts    # Pinia dashboard state and optimistic updates
    views/DashboardView.vue
    styles.css
  backend/
    app.py                 # Optional Flask mock API
    models.py              # Dataclass API models
    services.py            # In-memory sanitized mock data service
    tests/
  index.html
```

The frontend is the primary demo. It can run entirely in the browser with mock data and LocalStorage. The optional backend mirrors the public API shape for reviewers who want to inspect a simple full-stack boundary.

## Mocked Or Removed

- External trading API integrations were removed
- Real account identifiers, balances, logs, credentials, and server URLs were replaced with mock data
- Private strategy rules were replaced with simple A/B profile settings
- Order execution and account session automation are not included
- Logs are sanitized and generated for demonstration only
- The admin key input is stored locally for demo UI purposes only

## Screenshots

Add screenshots here after running the app locally:

```text
docs/screenshots/dashboard-overview.png
docs/screenshots/holdings-and-profiles.png
docs/screenshots/log-viewer.png
```

## How To Run

Install dependencies:

```bash
npm install
```

Start the frontend:

```bash
npm run dev
```

Build for production:

```bash
npm run build
```

Run the optional Python mock backend:

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r backend/requirements.txt
python -m backend.app
```

Run backend tests:

```bash
python -m unittest discover backend/tests
```

## API Shape

The optional backend exposes a sanitized mock API:

| Method | Endpoint | Description |
| --- | --- | --- |
| GET | `/api/health` | Health check |
| GET | `/api/dashboard` | Aggregated dashboard snapshot |
| GET | `/api/accounts?status=Active` | Account list with optional status filter |
| GET | `/api/holdings?accountId=OPS-001` | Holdings with optional account filter |
| POST | `/api/strategies/<id>` | Update mock A/B profile configuration |
| GET | `/api/logs` | Sanitized operations logs |
| GET | `/api/servers` | Mock service status cards |

## Portfolio Notes

This repository is designed for public review. It demonstrates frontend architecture, dashboard UX, typed data modeling, state management, cache behavior, and mock full-stack boundaries without exposing sensitive financial systems or private operational details.
