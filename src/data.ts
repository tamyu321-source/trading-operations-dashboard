export type AccountStatus = "Live" | "Paused" | "Review";
export type RiskLevel = "Low" | "Medium" | "High";
export type OrderSide = "Buy" | "Sell";
export type OrderState = "Filled" | "Working" | "Rejected";
export type RpaAction = "refresh_positions" | "sync_orders" | "export_statement";
export type RpaStatus = "Queued" | "Running" | "Completed" | "Blocked" | "Failed";

export interface Account {
  id: string;
  name: string;
  desk: string;
  status: AccountStatus;
  equity: number;
  cash: number;
  exposure: number;
  dailyPnl: number;
  riskLevel: RiskLevel;
  activeOrders: number;
}

export interface Position {
  symbol: string;
  name: string;
  market: string;
  quantity: number;
  avgCost: number;
  last: number;
  dayPnl: number;
  exposure: number;
  strategy: string;
}

export interface RiskEvent {
  id: string;
  level: RiskLevel;
  title: string;
  owner: string;
  createdAt: string;
  detail: string;
}

export interface ExecutionEvent {
  time: string;
  account: string;
  symbol: string;
  side: OrderSide;
  quantity: number;
  state: OrderState;
  note: string;
}

export interface StrategyControl {
  id: string;
  name: string;
  mode: "Auto" | "Manual";
  guardrail: string;
  enabled: boolean;
}

export interface RpaCommand {
  id: string;
  accountId: string;
  action: RpaAction;
  status: RpaStatus;
  createdAt: string;
  operator: string;
  message: string;
  steps: string[];
  progress: number;
  currentStep: string;
  artifactUrl: string;
  logs: string[];
}

export interface DashboardPayload {
  asOf?: string;
  currency: string;
  summary?: {
    totalEquity: number;
    totalCash: number;
    totalPnl: number;
    activeOrders: number;
    averageExposure: number;
    riskItems: number;
  };
  accounts: Account[];
  positions: Position[];
  riskEvents: RiskEvent[];
  executions: ExecutionEvent[];
  strategies: StrategyControl[];
  rpaCommands?: RpaCommand[];
}

export const accounts: Account[] = [
  {
    id: "SG-ALPHA",
    name: "Alpha Growth",
    desk: "Cash Equity",
    status: "Live",
    equity: 1268400,
    cash: 284600,
    exposure: 78,
    dailyPnl: 18420,
    riskLevel: "Low",
    activeOrders: 6
  },
  {
    id: "SG-BETA",
    name: "Beta Income",
    desk: "Credit Portfolio",
    status: "Review",
    equity: 842300,
    cash: 103900,
    exposure: 84,
    dailyPnl: -4260,
    riskLevel: "Medium",
    activeOrders: 3
  },
  {
    id: "HK-DELTA",
    name: "Delta Tactical",
    desk: "Regional Basket",
    status: "Paused",
    equity: 673200,
    cash: 219400,
    exposure: 61,
    dailyPnl: 3920,
    riskLevel: "Low",
    activeOrders: 0
  }
];

export const positions: Position[] = [
  {
    symbol: "D05.SI",
    name: "DBS Group",
    market: "SGX",
    quantity: 8200,
    avgCost: 38.12,
    last: 39.46,
    dayPnl: 10988,
    exposure: 323572,
    strategy: "Momentum Guard"
  },
  {
    symbol: "O39.SI",
    name: "OCBC Bank",
    market: "SGX",
    quantity: 16400,
    avgCost: 14.91,
    last: 14.72,
    dayPnl: -3116,
    exposure: 241408,
    strategy: "Mean Reversion"
  },
  {
    symbol: "0700.HK",
    name: "Tencent",
    market: "HKEX",
    quantity: 2400,
    avgCost: 365.2,
    last: 372.4,
    dayPnl: 17280,
    exposure: 893760,
    strategy: "Breakout Ladder"
  },
  {
    symbol: "AAPL",
    name: "Apple",
    market: "NASDAQ",
    quantity: 980,
    avgCost: 187.4,
    last: 185.9,
    dayPnl: -1470,
    exposure: 182182,
    strategy: "US Overlay"
  }
];

export const riskEvents: RiskEvent[] = [
  {
    id: "R-1042",
    level: "Medium",
    title: "Exposure threshold approaching",
    owner: "Ops Lead",
    createdAt: "09:42",
    detail: "Beta Income is within 6% of the configured exposure cap."
  },
  {
    id: "R-1039",
    level: "Low",
    title: "Stale quote recovered",
    owner: "System",
    createdAt: "09:18",
    detail: "HKEX market data feed recovered after one delayed tick."
  },
  {
    id: "R-1031",
    level: "High",
    title: "Manual approval required",
    owner: "Trader",
    createdAt: "08:57",
    detail: "One sell order exceeded the standard participation guardrail."
  }
];

export const executions: ExecutionEvent[] = [
  {
    time: "10:14:23",
    account: "Alpha Growth",
    symbol: "D05.SI",
    side: "Sell",
    quantity: 1200,
    state: "Filled",
    note: "Target trim completed"
  },
  {
    time: "10:09:11",
    account: "Beta Income",
    symbol: "O39.SI",
    side: "Buy",
    quantity: 2400,
    state: "Working",
    note: "Limit order inside spread"
  },
  {
    time: "09:58:44",
    account: "Delta Tactical",
    symbol: "0700.HK",
    side: "Sell",
    quantity: 600,
    state: "Rejected",
    note: "Paused account protection"
  },
  {
    time: "09:41:02",
    account: "Alpha Growth",
    symbol: "AAPL",
    side: "Buy",
    quantity: 180,
    state: "Filled",
    note: "US overlay rebalance"
  }
];

export const strategyControls: StrategyControl[] = [
  {
    id: "momentum",
    name: "Momentum Guard",
    mode: "Auto",
    guardrail: "Max 18% single-name exposure",
    enabled: true
  },
  {
    id: "reversion",
    name: "Mean Reversion",
    mode: "Auto",
    guardrail: "Requires spread below 12 bps",
    enabled: true
  },
  {
    id: "manual-review",
    name: "Manual Review",
    mode: "Manual",
    guardrail: "Trader approval for exceptions",
    enabled: false
  }
];

export const rpaCommands: RpaCommand[] = [
  {
    id: "RPA-2401",
    accountId: "SG-ALPHA",
    action: "refresh_positions",
    status: "Completed",
    createdAt: "10:16:12",
    operator: "System",
    message: "Position refresh completed through the broker desktop workflow.",
    steps: ["Focus broker window", "Open holdings tab", "Trigger refresh", "Read updated table"],
    progress: 100,
    currentStep: "Read updated table",
    artifactUrl: "",
    logs: ["10:16:12 Scheduler accepted command", "10:16:13 Completed holdings refresh"]
  }
];

export const fallbackDashboard: DashboardPayload = {
  currency: "SGD",
  accounts,
  positions,
  riskEvents,
  executions,
  strategies: strategyControls,
  rpaCommands
};
