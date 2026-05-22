from __future__ import annotations

from copy import deepcopy
from datetime import datetime, timedelta, timezone
from statistics import mean
from threading import Lock

from .models import Account, Holding, OpsLog, ServerCard, StrategyProfile


class TradingOperationsService:
    """In-memory mock API for the public portfolio dashboard."""

    def __init__(self) -> None:
        self._lock = Lock()
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
            ServerCard("ops-feed", "Mock Ops Feed", "Simulated", "Degraded", 168, 7, "10:17:58"),
        ]

    def dashboard(self) -> dict:
        with self._lock:
            accounts = [item.to_dict() for item in self._accounts]
            holdings = [item.to_dict() for item in self._holdings]
            strategies = [item.to_dict() for item in self._strategies]
            logs = [item.to_dict() for item in self._logs]
            servers = [item.to_dict() for item in self._servers]

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

    def _log(self, level: str, source: str, message: str) -> OpsLog:
        return OpsLog(f"LOG-{int(datetime.now().timestamp())}", level, source, message, self._now_time())  # type: ignore[arg-type]

    def _now_time(self) -> str:
        return datetime.now(timezone(timedelta(hours=8))).strftime("%H:%M:%S")
