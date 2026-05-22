# Trading Operations Dashboard

An English, portfolio-ready full-stack trading operations dashboard inspired by a real multi-account stock trading console. The project focuses on the parts that are useful to show publicly on GitHub: product thinking, Python API design, operational workflows, risk visibility, responsive UI, and clean Vue + TypeScript implementation.

> This repository uses simulated data only. It does not include broker credentials, private account data, RPA scripts, or proprietary trading rules.

## Why This Project

I built this project to present my experience with trading workflow automation in a recruiter-friendly format for Singapore-based software engineering and fintech roles. It translates a practical internal tool into a public demo that can be reviewed safely.

## Features

- Multi-account supervision with account status, cash, exposure, active orders, and daily P&L
- Portfolio position table covering SGX, HKEX, and US instruments
- Risk queue for operational exceptions and manual approval workflows
- Strategy control panel for automated and manual trading modes
- Execution tape showing order lifecycle states
- Python Flask backend with typed service and model layers
- REST endpoints for dashboard snapshots, accounts, risk events, and strategy toggles
- Backend RPA scheduler that validates account state, queues desktop automation commands, runs them in a background worker, updates progress, writes logs, and generates artifacts
- Frontend interactions that call backend APIs: dashboard refresh, account status filtering, risk level filtering, and strategy toggles
- English / Simplified Chinese / Traditional Chinese UI language switch for international portfolio review
- Responsive dashboard layout for desktop and mobile review
- Fully English UI and documentation

## Tech Stack

- Python 3
- Flask
- Vue 3
- TypeScript
- Vite
- CSS Grid and responsive CSS
- Simulated trading operations data model

## Getting Started

Start the Python backend:

```bash
cd trading-operations-dashboard
python -m venv .venv
.venv\Scripts\activate
pip install -r backend/requirements.txt
python -m backend.app
```

The backend runs on `http://127.0.0.1:8000`.

In a second terminal, start the Vue frontend:

```bash
npm install
npm run dev
```

Then open the local URL printed by Vite. During development, Vite proxies `/api` requests to the Python backend.

Run checks:

```bash
npm run build
python -m unittest discover backend/tests
```

Build the frontend for production:

```bash
npm run build
```

If the frontend is served separately from the backend, set `VITE_API_BASE_URL` in `.env`:

```bash
VITE_API_BASE_URL=http://127.0.0.1:8000
```

## API Overview

| Method | Endpoint | Description |
| --- | --- | --- |
| GET | `/api/health` | Service health check |
| GET | `/api/dashboard` | Aggregated dashboard snapshot |
| GET | `/api/accounts?status=Live` | Account list with optional status filter |
| GET | `/api/risk-events?level=High` | Risk queue with optional level filter |
| POST | `/api/strategies/<id>/toggle` | Toggle a strategy control |
| GET | `/api/rpa/commands` | List RPA task queue and audit records |
| POST | `/api/rpa/commands` | Submit a guarded RPA task for a selected account |
| GET | `/api/rpa/artifacts/<filename>` | Download generated RPA output artifacts |

## Backend Integration In The UI

- The main dashboard refresh button calls `GET /api/dashboard`.
- The account status segmented control calls `GET /api/accounts?status=...`.
- The risk level segmented control calls `GET /api/risk-events?level=...`.
- Strategy switches call `POST /api/strategies/<id>/toggle`.
- The RPA Operations panel calls `POST /api/rpa/commands`, then polls `GET /api/rpa/commands` to show scheduler status, progress, logs, workflow steps, and generated artifacts.
- The sidebar displays whether the UI is connected to the live Python API or using offline fallback data.
- The hero language switch toggles the UI between English, Simplified Chinese, and Traditional Chinese.

## RPA Demo Scope

The RPA layer is intentionally safe for GitHub. It does not automate a real broker desktop session. Instead, it demonstrates the backend task-management pattern used for RPA systems:

- validate account state before desktop automation
- accept a limited set of command types
- enqueue commands into a backend scheduler
- run commands asynchronously in a worker thread
- transition tasks through `Queued`, `Running`, `Completed`, and `Blocked`
- expose ordered workflow steps, progress, and execution logs
- generate downloadable artifacts such as holdings CSV and order/statement JSON
- keep an auditable command log for operations review

## Project Structure

```text
trading-operations-dashboard/
  backend/
    app.py        # Flask application factory and API routes
    models.py     # Dataclass-based API models
    services.py   # Trading operations service layer
    tests/        # Backend API tests
  src/
    App.vue       # Main dashboard experience
    api.ts        # Frontend API client
    data.ts       # Typed fallback demo data model
    main.ts       # Vue entry point
    styles.css    # Responsive UI styling
  index.html
  package.json
  README.md
```

## Deployment

The recommended production shape is:

- build the Vue frontend into static files
- run the Flask backend as an internal API service
- serve `dist/` and reverse-proxy `/api/*` through Nginx

### 1. Prepare A Linux Server

Example for Ubuntu:

```bash
sudo apt update
sudo apt install -y python3 python3-venv python3-pip nodejs npm nginx git
git clone <your-repo-url>
cd trading-operations-dashboard
```

Use Node 18+ if your server package manager installs an older Node version. The project currently uses Vite 4 for broad compatibility, but Node 18+ is still recommended for production builds.

### 2. Run The Backend

Create a Python virtual environment and install backend dependencies:

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r backend/requirements.txt
```

For a simple demo server:

```bash
python -m backend.app
```

For a more production-like Linux deployment, install Gunicorn:

```bash
pip install gunicorn
gunicorn "backend.app:app" --bind 127.0.0.1:8000 --workers 1 --threads 4
```

Use one worker for this demo because the in-memory RPA scheduler queue lives inside the backend process. In a real production system, move the queue to Redis/Celery/RQ or a database-backed job table before scaling to multiple workers.

### 3. Build The Frontend

If Nginx serves the frontend and proxies `/api` from the same domain, leave `VITE_API_BASE_URL` empty:

```bash
npm install
npm run build
```

If the backend is hosted on a different domain, create `.env.production` before building:

```bash
VITE_API_BASE_URL=https://api.example.com
npm run build
```

The static frontend output will be in `dist/`.

### 4. Nginx Reverse Proxy

Example Nginx site config:

```nginx
server {
    listen 80;
    server_name example.com;

    root /var/www/trading-operations-dashboard/dist;
    index index.html;

    location / {
        try_files $uri $uri/ /index.html;
    }

    location /api/ {
        proxy_pass http://127.0.0.1:8000/api/;
        proxy_http_version 1.1;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

Then enable and reload Nginx:

```bash
sudo nginx -t
sudo systemctl reload nginx
```

### 5. Optional systemd Service

Create `/etc/systemd/system/trading-ops-api.service`:

```ini
[Unit]
Description=Trading Operations Dashboard API
After=network.target

[Service]
WorkingDirectory=/var/www/trading-operations-dashboard
Environment="PYTHONUNBUFFERED=1"
ExecStart=/var/www/trading-operations-dashboard/.venv/bin/gunicorn backend.app:app --bind 127.0.0.1:8000 --workers 1 --threads 4
Restart=always
RestartSec=3

[Install]
WantedBy=multi-user.target
```

Start it:

```bash
sudo systemctl daemon-reload
sudo systemctl enable trading-ops-api
sudo systemctl start trading-ops-api
sudo systemctl status trading-ops-api
```

### 6. Windows Server Deployment

Gunicorn does not run natively on Windows. For a Windows demo server, use Waitress for the Flask backend and serve the frontend with IIS, Nginx for Windows, or another static file server.

Open PowerShell and prepare the project:

```powershell
git clone <your-repo-url>
cd trading-operations-dashboard
py -3 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r backend\requirements.txt
pip install waitress
```

Start the backend API:

```bash
waitress-serve --listen=127.0.0.1:8000 backend.app:app
```

Build the frontend:

```powershell
npm install
npm run build
```

The built frontend is in:

```text
trading-operations-dashboard\dist
```

#### Option A: Nginx For Windows

Download Nginx for Windows from the official Nginx site, extract it, and configure `conf/nginx.conf`:

```nginx
server {
    listen 80;
    server_name localhost;

    root C:/path/to/trading-operations-dashboard/dist;
    index index.html;

    location / {
        try_files $uri $uri/ /index.html;
    }

    location /api/ {
        proxy_pass http://127.0.0.1:8000/api/;
        proxy_http_version 1.1;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

Start Nginx:

```powershell
cd C:\nginx
start nginx
```

Reload after config changes:

```powershell
.\nginx.exe -s reload
```

#### Option B: IIS

1. Install IIS and the URL Rewrite module.
2. Point an IIS site to `trading-operations-dashboard\dist`.
3. Add a reverse proxy rule for `/api/*` to `http://127.0.0.1:8000/api/*`.
4. Make sure `index.html` is the fallback document for client-side routing.

#### Optional Windows Service

For a more stable Windows demo server, run Waitress through NSSM:

```powershell
nssm install TradingOpsApi
```

Use these values in NSSM:

```text
Application path: C:\path\to\trading-operations-dashboard\.venv\Scripts\waitress-serve.exe
Startup directory: C:\path\to\trading-operations-dashboard
Arguments: --listen=127.0.0.1:8000 backend.app:app
```

Then start the service:

```powershell
nssm start TradingOpsApi
```

If Windows blocks local traffic, allow the chosen HTTP port in Windows Defender Firewall.

### Deployment Notes

- This demo uses in-memory data and an in-process RPA scheduler.
- Generated RPA artifacts are written under `backend/artifacts/`.
- For real production use, persist accounts, jobs, logs, and artifacts in a database/object storage.
- Add authentication before exposing any RPA control endpoints publicly.
- Put the site behind HTTPS when deploying outside a private network.

## Design Notes

The dashboard is intentionally operational rather than marketing-oriented. It prioritizes dense but readable information, clear controls, visible risk states, and fast scanning. This mirrors the way trading and operations teams review account health, outstanding orders, and exception queues during a market session.

## Public Demo Scope

The original private system includes deeper automation around account sessions, position refresh, order execution, statistics, and Windows desktop workflow integration. This GitHub version is a safe presentation layer that demonstrates the product surface and engineering style without exposing private integrations.
