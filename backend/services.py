from __future__ import annotations

from copy import deepcopy
from datetime import datetime, timedelta, timezone
import csv
import json
from pathlib import Path
from queue import Queue
from statistics import mean
from threading import Lock, Thread
from time import sleep

from .models import Account, ExecutionEvent, Position, RiskEvent, RpaCommand, StrategyControl


class TradingOperationsService:
    """In-memory service layer that mirrors production trading dashboard boundaries."""

    def __init__(self) -> None:
        self._lock = Lock()
        self._rpa_queue: Queue[str] = Queue()
        self._artifact_dir = Path(__file__).resolve().parent / "artifacts"
        self._artifact_dir.mkdir(exist_ok=True)
        self._accounts = [
            Account("SG-ALPHA", "Alpha Growth", "Cash Equity", "Live", 1268400, 284600, 78, 18420, "Low", 6),
            Account("SG-BETA", "Beta Income", "Credit Portfolio", "Review", 842300, 103900, 84, -4260, "Medium", 3),
            Account("HK-DELTA", "Delta Tactical", "Regional Basket", "Paused", 673200, 219400, 61, 3920, "Low", 0),
        ]
        self._positions = [
            Position("D05.SI", "DBS Group", "SGX", 8200, 38.12, 39.46, 10988, 323572, "Momentum Guard"),
            Position("O39.SI", "OCBC Bank", "SGX", 16400, 14.91, 14.72, -3116, 241408, "Mean Reversion"),
            Position("0700.HK", "Tencent", "HKEX", 2400, 365.2, 372.4, 17280, 893760, "Breakout Ladder"),
            Position("AAPL", "Apple", "NASDAQ", 980, 187.4, 185.9, -1470, 182182, "US Overlay"),
        ]
        self._risk_events = [
            RiskEvent(
                "R-1042",
                "Medium",
                "Exposure threshold approaching",
                "Ops Lead",
                "09:42",
                "Beta Income is within 6% of the configured exposure cap.",
            ),
            RiskEvent(
                "R-1039",
                "Low",
                "Stale quote recovered",
                "System",
                "09:18",
                "HKEX market data feed recovered after one delayed tick.",
            ),
            RiskEvent(
                "R-1031",
                "High",
                "Manual approval required",
                "Trader",
                "08:57",
                "One sell order exceeded the standard participation guardrail.",
            ),
        ]
        self._executions = [
            ExecutionEvent("10:14:23", "Alpha Growth", "D05.SI", "Sell", 1200, "Filled", "Target trim completed"),
            ExecutionEvent("10:09:11", "Beta Income", "O39.SI", "Buy", 2400, "Working", "Limit order inside spread"),
            ExecutionEvent("09:58:44", "Delta Tactical", "0700.HK", "Sell", 600, "Rejected", "Paused account protection"),
            ExecutionEvent("09:41:02", "Alpha Growth", "AAPL", "Buy", 180, "Filled", "US overlay rebalance"),
        ]
        self._strategies = [
            StrategyControl("momentum", "Momentum Guard", "Auto", "Max 18% single-name exposure", True),
            StrategyControl("reversion", "Mean Reversion", "Auto", "Requires spread below 12 bps", True),
            StrategyControl("manual-review", "Manual Review", "Manual", "Trader approval for exceptions", False),
        ]
        self._rpa_commands = [
            RpaCommand(
                "RPA-2401",
                "SG-ALPHA",
                "refresh_positions",
                "Completed",
                "10:16:12",
                "System",
                "Position refresh completed through the broker desktop workflow.",
                ["Focus broker window", "Open holdings tab", "Trigger refresh", "Read updated table"],
                100,
                "Read updated table",
                "",
                ["10:16:12 Scheduler accepted command", "10:16:13 Completed holdings refresh"],
            )
        ]
        self._worker = Thread(target=self._rpa_worker, name="rpa-scheduler", daemon=True)
        self._worker.start()

    def dashboard(self) -> dict:
        with self._lock:
            accounts = [item.to_dict() for item in self._accounts]
            positions = [item.to_dict() for item in self._positions]
            risk_events = [item.to_dict() for item in self._risk_events]
            executions = [item.to_dict() for item in self._executions]
            strategies = [item.to_dict() for item in self._strategies]
            rpa_commands = [item.to_dict() for item in self._rpa_commands]

        total_equity = sum(item.equity for item in self._accounts)
        total_cash = sum(item.cash for item in self._accounts)
        total_pnl = sum(item.dailyPnl for item in self._accounts)
        active_orders = sum(item.activeOrders for item in self._accounts)
        average_exposure = round(mean(item.exposure for item in self._accounts), 1)

        return {
            "asOf": datetime.now(timezone(timedelta(hours=8))).isoformat(timespec="seconds"),
            "currency": "SGD",
            "summary": {
                "totalEquity": total_equity,
                "totalCash": total_cash,
                "totalPnl": total_pnl,
                "activeOrders": active_orders,
                "averageExposure": average_exposure,
                "riskItems": len([item for item in self._risk_events if item.level != "Low"]),
            },
            "accounts": accounts,
            "positions": positions,
            "riskEvents": risk_events,
            "executions": executions,
            "strategies": strategies,
            "rpaCommands": rpa_commands,
        }

    def accounts(self, status: str | None = None) -> list[dict]:
        with self._lock:
            rows = self._accounts
            if status and status != "All":
                rows = [item for item in rows if item.status == status]
            return [item.to_dict() for item in rows]

    def risk_events(self, level: str | None = None) -> list[dict]:
        with self._lock:
            rows = self._risk_events
            if level:
                rows = [item for item in rows if item.level == level]
            return [item.to_dict() for item in rows]

    def toggle_strategy(self, strategy_id: str, enabled: bool) -> dict:
        updated = []
        selected = None
        for item in self._strategies:
            if item.id == strategy_id:
                selected = StrategyControl(item.id, item.name, item.mode, item.guardrail, enabled)
                updated.append(selected)
            else:
                updated.append(item)

        if selected is None:
            raise KeyError(strategy_id)

        self._strategies = updated
        return deepcopy(selected.to_dict())

    def rpa_commands(self) -> list[dict]:
        with self._lock:
            return [item.to_dict() for item in self._rpa_commands]

    def submit_rpa_command(self, account_id: str, action: str, operator: str = "Portfolio Reviewer") -> dict:
        with self._lock:
            account = next((item for item in self._accounts if item.id == account_id), None)
            if account is None:
                raise KeyError(account_id)

        allowed_actions = {
            "refresh_positions": {
                "message": "Position refresh queued through the broker desktop workflow.",
                "steps": ["Focus broker window", "Open holdings tab", "Trigger refresh", "Read updated table"],
            },
            "sync_orders": {
                "message": "Order synchronization queued through the broker entrustment workflow.",
                "steps": ["Focus broker window", "Open order list", "Export working orders", "Normalize order states"],
            },
            "export_statement": {
                "message": "Statement export queued for back-office reconciliation.",
                "steps": ["Open statement center", "Select current trade date", "Export file", "Register audit record"],
            },
        }
        if action not in allowed_actions:
            raise ValueError(f"Unsupported RPA action: {action}")

        with self._lock:
            command_id = f"RPA-{2400 + len(self._rpa_commands) + 1}"
            created_at = datetime.now(timezone(timedelta(hours=8))).strftime("%H:%M:%S")

            if account.status == "Paused" and action != "export_statement":
                command = RpaCommand(
                    command_id,
                    account.id,
                    action,  # type: ignore[arg-type]
                    "Blocked",
                    created_at,
                    operator,
                    "Command blocked because the account is paused.",
                    ["Validate account status", "Stop before desktop automation"],
                    100,
                    "Stop before desktop automation",
                    "",
                    [f"{created_at} Scheduler blocked command before desktop automation"],
                )
                self._rpa_commands.insert(0, command)
                return deepcopy(command.to_dict())

            definition = allowed_actions[action]
            command = RpaCommand(
                command_id,
                account.id,
                action,  # type: ignore[arg-type]
                "Queued",
                created_at,
                operator,
                definition["message"],
                definition["steps"],
                0,
                "Waiting for scheduler",
                "",
                [f"{created_at} Scheduler accepted command"],
            )
            self._rpa_commands.insert(0, command)

        self._rpa_queue.put(command.id)
        return deepcopy(command.to_dict())

    def artifact_path(self, filename: str) -> Path:
        safe_name = Path(filename).name
        path = self._artifact_dir / safe_name
        if not path.exists():
            raise FileNotFoundError(safe_name)
        return path

    def _rpa_worker(self) -> None:
        while True:
            command_id = self._rpa_queue.get()
            try:
                self._execute_rpa_command(command_id)
            finally:
                self._rpa_queue.task_done()

    def _execute_rpa_command(self, command_id: str) -> None:
        command = self._find_command(command_id)
        if command is None:
            return

        self._update_command(command, status="Running", progress=5, current_step="Starting desktop automation")
        steps = list(command.steps)
        for index, step in enumerate(steps, start=1):
            self._update_command(
                command,
                status="Running",
                progress=min(90, int(index / max(len(steps), 1) * 85)),
                current_step=step,
                log=f"{self._now_time()} {step}",
            )
            sleep(0.35)

        try:
            artifact_url = self._perform_rpa_action(command)
            self._update_command(
                command,
                status="Completed",
                progress=100,
                current_step="Completed",
                artifact_url=artifact_url,
                log=f"{self._now_time()} Completed and wrote artifact {artifact_url}",
            )
        except Exception as exc:  # pragma: no cover - defensive scheduler boundary
            self._update_command(
                command,
                status="Failed",
                progress=100,
                current_step="Failed",
                log=f"{self._now_time()} Failed: {exc}",
            )

    def _find_command(self, command_id: str) -> RpaCommand | None:
        with self._lock:
            return next((item for item in self._rpa_commands if item.id == command_id), None)

    def _update_command(
        self,
        command: RpaCommand,
        *,
        status: str,
        progress: int,
        current_step: str,
        artifact_url: str | None = None,
        log: str | None = None,
    ) -> None:
        with self._lock:
            command.status = status  # type: ignore[assignment]
            command.progress = progress
            command.currentStep = current_step
            if artifact_url is not None:
                command.artifactUrl = artifact_url
            if log:
                if command.logs is None:
                    command.logs = []
                command.logs.append(log)

    def _perform_rpa_action(self, command: RpaCommand) -> str:
        if command.action == "refresh_positions":
            return self._write_positions_artifact(command)
        if command.action == "sync_orders":
            return self._write_orders_artifact(command)
        return self._write_statement_artifact(command)

    def _write_positions_artifact(self, command: RpaCommand) -> str:
        filename = f"{command.id}_holdings.csv"
        path = self._artifact_dir / filename
        with self._lock:
            updated_positions = []
            for position in self._positions:
                updated = Position(
                    position.symbol,
                    position.name,
                    position.market,
                    position.quantity,
                    position.avgCost,
                    round(position.last * 1.001, 2),
                    round(position.dayPnl + 125, 2),
                    position.exposure,
                    position.strategy,
                )
                updated_positions.append(updated)
            self._positions = updated_positions
            rows = [item.to_dict() for item in self._positions]

        with path.open("w", newline="", encoding="utf-8") as handle:
            writer = csv.DictWriter(handle, fieldnames=list(rows[0].keys()))
            writer.writeheader()
            writer.writerows(rows)
        return f"/api/rpa/artifacts/{filename}"

    def _write_orders_artifact(self, command: RpaCommand) -> str:
        filename = f"{command.id}_orders.json"
        path = self._artifact_dir / filename
        with self._lock:
            self._executions.insert(
                0,
                ExecutionEvent(self._now_time(), command.accountId, "D05.SI", "Sell", 500, "Working", "RPA order sync"),
            )
            rows = [item.to_dict() for item in self._executions]

        path.write_text(json.dumps(rows, indent=2), encoding="utf-8")
        return f"/api/rpa/artifacts/{filename}"

    def _write_statement_artifact(self, command: RpaCommand) -> str:
        filename = f"{command.id}_statement.json"
        path = self._artifact_dir / filename
        payload = {
            "accountId": command.accountId,
            "generatedAt": datetime.now(timezone(timedelta(hours=8))).isoformat(timespec="seconds"),
            "cashMovements": [
                {"type": "Trade settlement", "amount": 18420.0},
                {"type": "Fees", "amount": -82.6},
            ],
        }
        path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
        return f"/api/rpa/artifacts/{filename}"

    def _now_time(self) -> str:
        return datetime.now(timezone(timedelta(hours=8))).strftime("%H:%M:%S")
