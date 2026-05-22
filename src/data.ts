export type AccountStatus = "Active" | "Review" | "Paused";
export type RiskLevel = "Low" | "Medium" | "High";
export type SortDirection = "asc" | "desc";
export type ServerStatus = "Online" | "Degraded" | "Offline";
export type LogLevel = "info" | "warning" | "error";
export type ProfileVariant = "A" | "B";

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
  activeTickets: number;
}

export interface Holding {
  id: string;
  accountId: string;
  symbol: string;
  name: string;
  market: string;
  quantity: number;
  avgCost: number;
  last: number;
  exposure: number;
  dayPnl: number;
  profile: ProfileVariant;
}

export interface GroupedHolding {
  symbol: string;
  name: string;
  market: string;
  accounts: number;
  quantity: number;
  exposure: number;
  dayPnl: number;
  profiles: ProfileVariant[];
}

export interface StrategyProfile {
  id: string;
  label: string;
  variant: ProfileVariant;
  maxSingleNameExposure: number;
  rebalanceWindow: string;
  alertsEnabled: boolean;
  notes: string;
}

export interface OpsLog {
  id: string;
  level: LogLevel;
  source: string;
  message: string;
  timestamp: string;
}

export interface ServerStatusCard {
  id: string;
  name: string;
  region: string;
  status: ServerStatus;
  latencyMs: number;
  queueDepth: number;
  lastHeartbeat: string;
}

export interface DashboardPayload {
  asOf: string;
  accounts: Account[];
  holdings: Holding[];
  strategies: StrategyProfile[];
  logs: OpsLog[];
  servers: ServerStatusCard[];
}

export const demoAccounts: Account[] = [
  {
    id: "OPS-001",
    name: "Alpha Growth",
    desk: "Equity Ops",
    status: "Active",
    equity: 1268400,
    cash: 284600,
    exposure: 78,
    dailyPnl: 18420,
    riskLevel: "Low",
    activeTickets: 6
  },
  {
    id: "OPS-002",
    name: "Beta Income",
    desk: "Portfolio Ops",
    status: "Review",
    equity: 842300,
    cash: 103900,
    exposure: 84,
    dailyPnl: -4260,
    riskLevel: "Medium",
    activeTickets: 3
  },
  {
    id: "OPS-003",
    name: "Delta Tactical",
    desk: "Regional Ops",
    status: "Paused",
    equity: 673200,
    cash: 219400,
    exposure: 61,
    dailyPnl: 3920,
    riskLevel: "Low",
    activeTickets: 0
  },
  {
    id: "OPS-004",
    name: "Gamma Balanced",
    desk: "ETF Ops",
    status: "Active",
    equity: 934800,
    cash: 171250,
    exposure: 72,
    dailyPnl: 6840,
    riskLevel: "Low",
    activeTickets: 4
  }
];

export const demoHoldings: Holding[] = [
  {
    id: "H-1001",
    accountId: "OPS-001",
    symbol: "D05.SI",
    name: "DBS Group",
    market: "SGX",
    quantity: 8200,
    avgCost: 38.12,
    last: 39.46,
    dayPnl: 10988,
    exposure: 323572,
    profile: "A"
  },
  {
    id: "H-1002",
    accountId: "OPS-002",
    symbol: "D05.SI",
    name: "DBS Group",
    market: "SGX",
    quantity: 3300,
    avgCost: 38.02,
    last: 39.46,
    dayPnl: 4752,
    exposure: 130218,
    profile: "B"
  },
  {
    id: "H-1003",
    accountId: "OPS-001",
    symbol: "O39.SI",
    name: "OCBC Bank",
    market: "SGX",
    quantity: 16400,
    avgCost: 14.91,
    last: 14.72,
    dayPnl: -3116,
    exposure: 241408,
    profile: "A"
  },
  {
    id: "H-1004",
    accountId: "OPS-003",
    symbol: "0700.HK",
    name: "Tencent Holdings",
    market: "HKEX",
    quantity: 2400,
    avgCost: 365.2,
    last: 372.4,
    dayPnl: 17280,
    exposure: 893760,
    profile: "B"
  },
  {
    id: "H-1005",
    accountId: "OPS-004",
    symbol: "AAPL",
    name: "Apple",
    market: "NASDAQ",
    quantity: 980,
    avgCost: 187.4,
    last: 185.9,
    dayPnl: -1470,
    exposure: 182182,
    profile: "A"
  },
  {
    id: "H-1006",
    accountId: "OPS-004",
    symbol: "SPY",
    name: "S&P 500 ETF",
    market: "NYSE Arca",
    quantity: 510,
    avgCost: 521.8,
    last: 526.3,
    dayPnl: 2295,
    exposure: 268413,
    profile: "B"
  }
];

export const demoStrategies: StrategyProfile[] = [
  {
    id: "strategy-a",
    label: "Profile A",
    variant: "A",
    maxSingleNameExposure: 18,
    rebalanceWindow: "09:30-11:30",
    alertsEnabled: true,
    notes: "Conservative review settings for high-liquidity holdings."
  },
  {
    id: "strategy-b",
    label: "Profile B",
    variant: "B",
    maxSingleNameExposure: 24,
    rebalanceWindow: "13:00-15:00",
    alertsEnabled: true,
    notes: "Wider tolerance used for demo comparison workflows."
  }
];

export const demoServers: ServerStatusCard[] = [
  {
    id: "mock-api",
    name: "Mock REST API",
    region: "Local demo",
    status: "Online",
    latencyMs: 42,
    queueDepth: 2,
    lastHeartbeat: "10:18:24"
  },
  {
    id: "cache",
    name: "Browser Cache",
    region: "LocalStorage",
    status: "Online",
    latencyMs: 4,
    queueDepth: 0,
    lastHeartbeat: "10:18:21"
  },
  {
    id: "ops-feed",
    name: "Mock Ops Feed",
    region: "Simulated",
    status: "Degraded",
    latencyMs: 168,
    queueDepth: 7,
    lastHeartbeat: "10:17:58"
  }
];

export const demoLogs: OpsLog[] = [
  {
    id: "LOG-1004",
    level: "info",
    source: "mock-api",
    message: "Dashboard snapshot refreshed with sanitized portfolio data.",
    timestamp: "10:18:24"
  },
  {
    id: "LOG-1003",
    level: "warning",
    source: "ops-feed",
    message: "Beta Income requires review because exposure is near its demo threshold.",
    timestamp: "10:16:42"
  },
  {
    id: "LOG-1002",
    level: "info",
    source: "cache",
    message: "Strategy profile preferences restored from LocalStorage.",
    timestamp: "10:12:08"
  },
  {
    id: "LOG-1001",
    level: "error",
    source: "mock-api",
    message: "One simulated status check returned a retryable timeout.",
    timestamp: "10:08:55"
  }
];

export const fallbackDashboard: DashboardPayload = {
  asOf: new Date().toISOString(),
  accounts: demoAccounts,
  holdings: demoHoldings,
  strategies: demoStrategies,
  logs: demoLogs,
  servers: demoServers
};
