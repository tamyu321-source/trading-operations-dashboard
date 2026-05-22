import {
  fallbackDashboard,
  type Account,
  type AccountStatus,
  type DashboardPayload,
  type RiskEvent,
  type RiskLevel,
  type RpaAction,
  type RpaCommand,
  type StrategyControl
} from "./data";

const API_BASE = import.meta.env.VITE_API_BASE_URL || "";

export async function fetchDashboard(): Promise<DashboardPayload> {
  const response = await fetch(`${API_BASE}/api/dashboard`);
  if (!response.ok) {
    throw new Error(`Dashboard API returned HTTP ${response.status}`);
  }

  const payload = (await response.json()) as { data?: DashboardPayload };
  return payload.data || fallbackDashboard;
}

export async function fetchAccounts(status: "All" | AccountStatus): Promise<Account[]> {
  const query = status === "All" ? "" : `?status=${encodeURIComponent(status)}`;
  const response = await fetch(`${API_BASE}/api/accounts${query}`);
  if (!response.ok) {
    throw new Error(`Accounts API returned HTTP ${response.status}`);
  }

  const payload = (await response.json()) as { data?: Account[] };
  return payload.data || fallbackDashboard.accounts;
}

export async function fetchRiskEvents(level: "All" | RiskLevel): Promise<RiskEvent[]> {
  const query = level === "All" ? "" : `?level=${encodeURIComponent(level)}`;
  const response = await fetch(`${API_BASE}/api/risk-events${query}`);
  if (!response.ok) {
    throw new Error(`Risk API returned HTTP ${response.status}`);
  }

  const payload = (await response.json()) as { data?: RiskEvent[] };
  return payload.data || fallbackDashboard.riskEvents;
}

export async function toggleStrategy(strategy: StrategyControl): Promise<StrategyControl> {
  const response = await fetch(`${API_BASE}/api/strategies/${strategy.id}/toggle`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ enabled: strategy.enabled })
  });

  if (!response.ok) {
    throw new Error(`Strategy API returned HTTP ${response.status}`);
  }

  const payload = (await response.json()) as { data: StrategyControl };
  return payload.data;
}

export async function fetchRpaCommands(): Promise<RpaCommand[]> {
  const response = await fetch(`${API_BASE}/api/rpa/commands`);
  if (!response.ok) {
    throw new Error(`RPA API returned HTTP ${response.status}`);
  }

  const payload = (await response.json()) as { data?: RpaCommand[] };
  return payload.data || fallbackDashboard.rpaCommands || [];
}

export async function submitRpaCommand(accountId: string, action: RpaAction): Promise<RpaCommand> {
  const response = await fetch(`${API_BASE}/api/rpa/commands`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ accountId, action, operator: "Dashboard Demo" })
  });

  if (!response.ok) {
    throw new Error(`RPA API returned HTTP ${response.status}`);
  }

  const payload = (await response.json()) as { data: RpaCommand };
  return payload.data;
}
