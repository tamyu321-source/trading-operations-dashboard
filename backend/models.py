from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Literal


AccountStatus = Literal["Active", "Paused", "Review"]
RiskLevel = Literal["Low", "Medium", "High"]
ProfileVariant = Literal["A", "B"]
ServerStatus = Literal["Online", "Degraded", "Offline"]
LogLevel = Literal["info", "warning", "error"]
RpaAction = Literal["refresh_holdings", "reconcile_cash", "generate_report"]
RpaStatus = Literal["Queued", "Running", "Completed", "Blocked", "Failed"]


@dataclass(frozen=True)
class Account:
    id: str
    name: str
    desk: str
    status: AccountStatus
    equity: float
    cash: float
    exposure: int
    dailyPnl: float
    riskLevel: RiskLevel
    activeTickets: int

    def to_dict(self) -> dict:
        return asdict(self)


@dataclass(frozen=True)
class Holding:
    id: str
    accountId: str
    symbol: str
    name: str
    market: str
    quantity: int
    avgCost: float
    last: float
    exposure: float
    dayPnl: float
    profile: ProfileVariant

    def to_dict(self) -> dict:
        return asdict(self)


@dataclass(frozen=True)
class StrategyProfile:
    id: str
    label: str
    variant: ProfileVariant
    maxSingleNameExposure: int
    rebalanceWindow: str
    alertsEnabled: bool
    notes: str

    def to_dict(self) -> dict:
        return asdict(self)


@dataclass(frozen=True)
class OpsLog:
    id: str
    level: LogLevel
    source: str
    message: str
    timestamp: str

    def to_dict(self) -> dict:
        return asdict(self)


@dataclass(frozen=True)
class ServerCard:
    id: str
    name: str
    region: str
    status: ServerStatus
    latencyMs: int
    queueDepth: int
    lastHeartbeat: str

    def to_dict(self) -> dict:
        return asdict(self)


@dataclass
class RpaJob:
    id: str
    accountId: str
    action: RpaAction
    status: RpaStatus
    createdAt: str
    operator: str
    message: str
    steps: list[str]
    progress: int = 0
    currentStep: str = "Waiting for scheduler"
    artifactUrl: str = ""
    logs: list[str] | None = None

    def to_dict(self) -> dict:
        data = asdict(self)
        data["logs"] = data["logs"] or []
        return data
