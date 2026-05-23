from __future__ import annotations

from copy import deepcopy
from datetime import datetime, timedelta, timezone
import json
from pathlib import Path
from queue import Queue
from statistics import mean
from threading import Lock, Thread
from time import sleep

from .models import Account, Holding, OpsLog, RpaJob, ServerCard, StrategyProfile


class TradingOperationsService:
    """In-memory mock API for the public portfolio dashboard."""

    def __init__(self) -> None:
        self._lock = Lock()
        self._rpa_queue: Queue[str] = Queue()
        self._artifact_dir = Path(__file__).resolve().parent / "artifacts"
        self._artifact_dir.mkdir(exist_ok=True)
        self._accounts = [
            Account("OPS-001", "Alpha Growth", "Equity Ops", "Active", 1268400, 284600, 78, 18420, "Low", 6),
            Account("OPS-002", "Beta Income", "Portfolio Ops", "Review", 842300, 103900, 84, -4260, "Medium", 3),
            Account("OPS-003", "Delta Tactical", "Regional Ops", "Paused", 673200, 219400, 61, 3920, "Low", 0),
            Account("OPS-004", "Gamma Balanced", "ETF Ops", "Active", 934800, 171250, 72, 6840, "Low", 4),
        ]
        self._holdings = [
            Holding("H-1001", "OPS-001", "D05.SI", "DBS Group", "SGX", 8200, 38.12, 39.46, 323572, 10988, "A"),
            Holding("H-1002", "OPS-002", "D05.SI", "DBS Group", "SGX", 3300, 38.02, 39.46, 130218, 4752, "B"),
            Holding("H-1003", "OPS-001", "O39.SI", "OCBC Bank", "SGX", 16400, 14.91, 14.72, 241408, -3116, "A"),
            Holding("H-1004", "OPS-003", "0700.HK", "Tencent Holdings", "HKEX", 2400, 365.2, 372.4, 893760, 17280, "B"),
            Holding("H-1005", "OPS-004", "AAPL", "Apple", "NASDAQ", 980, 187.4, 185.9, 182182, -1470, "A"),
            Holding("H-1006", "OPS-004", "SPY", "S&P 500 ETF", "NYSE Arca", 510, 521.8, 526.3, 268413, 2295, "B"),
        ]
        self._strategies = [
            StrategyProfile(
                "strategy-a",
                "Profile A",
                "A",
                18,
                "09:30-11:30",
                True,
                "Conservative review settings for high-liquidity holdings.",
            ),
            StrategyProfile(
                "strategy-b",
                "Profile B",
                "B",
                24,
                "13:00-15:00",
                True,
                "Wider tolerance used for demo comparison workflows.",
            ),
        ]
        self._logs = [
            OpsLog("LOG-1004", "info", "mock-api", "Dashboard snapshot refreshed with sanitized portfolio data.", "10:18:24"),
            OpsLog("LOG-1003", "warning", "ops-feed", "Beta Income requires review near its demo threshold.", "10:16:42"),
            OpsLog("LOG-1002", "info", "cache", "Strategy profile preferences restored from local cache.", "10:12:08"),
            OpsLog("LOG-1001", "error", "mock-api", "One simulated status check returned a retryable timeout.", "10:08:55"),
        ]
        self._servers = [
            ServerCard("mock-api", "Mock REST API", "Local demo", "Online", 42, 2, "10:18:24"),
            ServerCard("cache", "Browser Cache", "LocalStorage", "Online", 4, 0, "10:18:21"),
            ServerCard("rpa-worker", "Mock RPA Worker", "Backend queue", "Online", 88, 1, "10:18:18"),
        ]
        self._rpa_jobs = [
            RpaJob(
                "RPA-3001",
                "OPS-001",
                "refresh_holdings",
                "Completed",
                "10:15:08",
                "Portfolio Reviewer",
                "Mock holdings refresh completed through the backend worker.",
                ["Validate demo account", "Read sanitized holdings", "Normalize rows", "Write review artifact"],
                100,
                "Completed",
                "/api/rpa/artifacts/RPA-3001_holdings_review.json",
                ["10:15:08 Accepted job", "10:15:09 Normalized 6 holdings", "10:15:10 Wrote mock artifact"],
            )
        ]
        self._write_seed_artifact()
        self._worker = Thread(target=self._rpa_worker, name="mock-rpa-worker", daemon=True)
        self._worker.start()

    def dashboard(self) -> dict:
        with self._lock:
            accounts = [item.to_dict() for item in self._accounts]
            holdings = [item.to_dict() for item in self._holdings]
            strategies = [item.to_dict() for item in self._strategies]
            logs = [item.to_dict() for item in self._logs]
            servers = [item.to_dict() for item in self._servers]
            rpa_jobs = [item.to_dict() for item in self._rpa_jobs]

        return {
            "asOf": datetime.now(timezone(timedelta(hours=8))).isoformat(timespec="seconds"),
            "summary": {
                "totalEquity": sum(item["equity"] for item in accounts),
                "totalCash": sum(item["cash"] for item in accounts),
                "totalPnl": sum(item["dailyPnl"] for item in accounts),
                "activeTickets": sum(item["activeTickets"] for item in accounts),
                "averageExposure": round(mean(item["exposure"] for item in accounts), 1),
            },
            "accounts": accounts,
            "holdings": holdings,
            "strategies": strategies,
            "logs": logs,
            "servers": servers,
            "rpaJobs": rpa_jobs,
        }

    def accounts(self, status: str | None = None) -> list[dict]:
        with self._lock:
            rows = self._accounts
            if status and status != "All":
                rows = [item for item in rows if item.status == status]
            return [item.to_dict() for item in rows]

    def holdings(self, account_id: str | None = None) -> list[dict]:
        with self._lock:
            rows = self._holdings
            if account_id and account_id != "All":
                rows = [item for item in rows if item.accountId == account_id]
            return [item.to_dict() for item in rows]

    def update_strategy(self, strategy_id: str, payload: dict) -> dict:
        with self._lock:
            updated = []
            selected = None
            for item in self._strategies:
                if item.id == strategy_id:
                    selected = StrategyProfile(
                        item.id,
                        str(payload.get("label", item.label)),
                        item.variant,
                        int(payload.get("maxSingleNameExposure", item.maxSingleNameExposure)),
                        str(payload.get("rebalanceWindow", item.rebalanceWindow)),
                        bool(payload.get("alertsEnabled", item.alertsEnabled)),
                        str(payload.get("notes", item.notes)),
                    )
                    updated.append(selected)
                else:
                    updated.append(item)

            if selected is None:
                raise KeyError(strategy_id)

            self._strategies = updated
            self._logs.insert(0, self._log("info", "mock-api", f"{selected.label} updated in mock API."))
            return deepcopy(selected.to_dict())

    def logs(self) -> list[dict]:
        with self._lock:
            return [item.to_dict() for item in self._logs]

    def servers(self) -> list[dict]:
        with self._lock:
            return [item.to_dict() for item in self._servers]

    def rpa_jobs(self) -> list[dict]:
        with self._lock:
            return [item.to_dict() for item in self._rpa_jobs]

    def submit_rpa_job(self, account_id: str, action: str, operator: str = "Portfolio Reviewer") -> dict:
        action_defs = {
            "refresh_holdings": {
                "message": "Mock holdings refresh queued for backend processing.",
                "steps": ["Validate demo account", "Read sanitized holdings", "Normalize rows", "Write review artifact"],
            },
            "reconcile_cash": {
                "message": "Mock cash reconciliation queued for backend processing.",
                "steps": ["Validate demo account", "Compare mock cash ledger", "Flag differences", "Write reconciliation note"],
            },
            "generate_report": {
                "message": "Mock operations report queued for backend processing.",
                "steps": ["Collect dashboard snapshot", "Summarize profile settings", "Attach server status", "Write report artifact"],
            },
        }
        if action not in action_defs:
            raise ValueError(f"Unsupported mock RPA action: {action}")

        with self._lock:
            account = next((item for item in self._accounts if item.id == account_id), None)
            if account is None:
                raise KeyError(account_id)

            created_at = self._now_time()
            job_id = f"RPA-{3000 + len(self._rpa_jobs) + 1}"
            if account.status == "Paused" and action != "generate_report":
                job = RpaJob(
                    job_id,
                    account.id,
                    action,  # type: ignore[arg-type]
                    "Blocked",
                    created_at,
                    operator,
                    "Mock RPA job blocked because the demo account is paused.",
                    ["Validate demo account", "Stop before worker task"],
                    100,
                    "Blocked by demo guardrail",
                    "",
                    [f"{created_at} Guardrail blocked the mock job"],
                )
                self._rpa_jobs.insert(0, job)
                return deepcopy(job.to_dict())

            definition = action_defs[action]
            job = RpaJob(
                job_id,
                account.id,
                action,  # type: ignore[arg-type]
                "Queued",
                created_at,
                operator,
                definition["message"],
                definition["steps"],
                logs=[f"{created_at} Accepted job into backend queue"],
            )
            self._rpa_jobs.insert(0, job)

        self._rpa_queue.put(job.id)
        return deepcopy(job.to_dict())

    def artifact_path(self, filename: str) -> Path:
        safe_name = Path(filename).name
        path = self._artifact_dir / safe_name
        if not path.exists():
            raise FileNotFoundError(safe_name)
        return path

    def _log(self, level: str, source: str, message: str) -> OpsLog:
        return OpsLog(f"LOG-{int(datetime.now().timestamp())}", level, source, message, self._now_time())  # type: ignore[arg-type]

    def _now_time(self) -> str:
        return datetime.now(timezone(timedelta(hours=8))).strftime("%H:%M:%S")

    def _rpa_worker(self) -> None:
        while True:
            job_id = self._rpa_queue.get()
            try:
                self._execute_rpa_job(job_id)
            finally:
                self._rpa_queue.task_done()

    def _execute_rpa_job(self, job_id: str) -> None:
        job = self._find_rpa_job(job_id)
        if job is None:
            return

        self._update_rpa_job(job, status="Running", progress=8, current_step="Starting backend worker")
        for index, step in enumerate(job.steps, start=1):
            self._update_rpa_job(
                job,
                status="Running",
                progress=min(92, int(index / max(len(job.steps), 1) * 86)),
                current_step=step,
                log=f"{self._now_time()} {step}",
            )
            sleep(0.45)

        artifact_url = self._write_rpa_artifact(job)
        self._update_rpa_job(
            job,
            status="Completed",
            progress=100,
            current_step="Completed",
            artifact_url=artifact_url,
            log=f"{self._now_time()} Completed mock RPA job",
        )
        with self._lock:
            self._logs.insert(0, self._log("info", "rpa-worker", f"{job.id} completed by backend worker."))

    def _find_rpa_job(self, job_id: str) -> RpaJob | None:
        with self._lock:
            return next((item for item in self._rpa_jobs if item.id == job_id), None)

    def _update_rpa_job(
        self,
        job: RpaJob,
        *,
        status: str,
        progress: int,
        current_step: str,
        artifact_url: str | None = None,
        log: str | None = None,
    ) -> None:
        with self._lock:
            job.status = status  # type: ignore[assignment]
            job.progress = progress
            job.currentStep = current_step
            if artifact_url is not None:
                job.artifactUrl = artifact_url
            if log:
                if job.logs is None:
                    job.logs = []
                job.logs.append(log)

    def _write_seed_artifact(self) -> None:
        path = self._artifact_dir / "RPA-3001_holdings_review.json"
        if path.exists():
            return
        payload = {
            "jobId": "RPA-3001",
            "scope": "sanitized portfolio demo",
            "summary": "Seed artifact generated for public portfolio review.",
        }
        path.write_text(json.dumps(payload, indent=2), encoding="utf-8")

    def _write_rpa_artifact(self, job: RpaJob) -> str:
        suffix = {
            "refresh_holdings": "holdings_review",
            "reconcile_cash": "cash_reconciliation",
            "generate_report": "operations_report",
        }[job.action]
        filename = f"{job.id}_{suffix}.json"
        path = self._artifact_dir / filename
        with self._lock:
            payload = {
                "jobId": job.id,
                "accountId": job.accountId,
                "action": job.action,
                "generatedAt": datetime.now(timezone(timedelta(hours=8))).isoformat(timespec="seconds"),
                "scope": "sanitized portfolio demo",
                "holdingsReviewed": len(self._holdings),
                "openTickets": sum(item.activeTickets for item in self._accounts),
                "note": "Mock artifact generated by the backend RPA worker. No external system was contacted.",
            }
        path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
        return f"/api/rpa/artifacts/{filename}"
