from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Literal


AccountStatus = Literal["Live", "Paused", "Review"]
RiskLevel = Literal["Low", "Medium", "High"]
OrderSide = Literal["Buy", "Sell"]
OrderState = Literal["Filled", "Working", "Rejected"]
RpaAction = Literal["refresh_positions", "sync_orders", "export_statement"]
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
    activeOrders: int

    def to_dict(self) -> dict:
        return asdict(self)


@dataclass(frozen=True)
class Position:
    symbol: str
    name: str
    market: str
    quantity: int
    avgCost: float
    last: float
    dayPnl: float
    exposure: float
    strategy: str

    def to_dict(self) -> dict:
        return asdict(self)


@dataclass(frozen=True)
class RiskEvent:
    id: str
    level: RiskLevel
    title: str
    owner: str
    createdAt: str
    detail: str

    def to_dict(self) -> dict:
        return asdict(self)


@dataclass(frozen=True)
class ExecutionEvent:
    time: str
    account: str
    symbol: str
    side: OrderSide
    quantity: int
    state: OrderState
    note: str

    def to_dict(self) -> dict:
        return asdict(self)


@dataclass(frozen=True)
class StrategyControl:
    id: str
    name: str
    mode: Literal["Auto", "Manual"]
    guardrail: str
    enabled: bool

    def to_dict(self) -> dict:
        return asdict(self)


@dataclass
class RpaCommand:
    id: str
    accountId: str
    action: RpaAction
    status: RpaStatus
    createdAt: str
    operator: str
    message: str
    steps: list[str]
    progress: int = 0
    currentStep: str = ""
    artifactUrl: str = ""
    logs: list[str] | None = None

    def to_dict(self) -> dict:
        data = asdict(self)
        data["logs"] = data["logs"] or []
        return data
