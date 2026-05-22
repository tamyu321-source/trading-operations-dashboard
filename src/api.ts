import {
  fallbackDashboard,
  type DashboardPayload,
  type Holding,
  type OpsLog,
  type ProfileVariant,
  type StrategyProfile
} from "./data";

const CACHE_KEY = "trading-ops-dashboard-cache";
const ADMIN_KEY = "trading-ops-demo-admin-key";

function cloneDashboard(): DashboardPayload {
  return JSON.parse(JSON.stringify(fallbackDashboard)) as DashboardPayload;
}

function readCache(): DashboardPayload | null {
  const raw = localStorage.getItem(CACHE_KEY);
  if (!raw) return null;

  try {
    return JSON.parse(raw) as DashboardPayload;
  } catch {
    localStorage.removeItem(CACHE_KEY);
    return null;
  }
}

function writeCache(payload: DashboardPayload) {
  localStorage.setItem(CACHE_KEY, JSON.stringify(payload));
}

function wait(ms = 380) {
  return new Promise((resolve) => window.setTimeout(resolve, ms));
}

export async function fetchMockDashboard(): Promise<DashboardPayload> {
  await wait();
  const cached = readCache();
  if (cached) return cached;

  const fresh = cloneDashboard();
  fresh.asOf = new Date().toISOString();
  writeCache(fresh);
  return fresh;
}

export async function saveStrategyProfile(profile: StrategyProfile): Promise<StrategyProfile> {
  await wait(220);
  const dashboard = readCache() || cloneDashboard();
  dashboard.strategies = dashboard.strategies.map((item) => (item.id === profile.id ? profile : item));
  dashboard.logs = [
    createLog("info", "strategy-ui", `${profile.label} saved optimistically in the mock service.`),
    ...dashboard.logs
  ].slice(0, 16);
  dashboard.asOf = new Date().toISOString();
  writeCache(dashboard);
  return profile;
}

export async function updateHoldingProfile(holdingId: string, profile: ProfileVariant): Promise<Holding> {
  await wait(260);
  const dashboard = readCache() || cloneDashboard();
  const holding = dashboard.holdings.find((item) => item.id === holdingId);
  if (!holding) {
    throw new Error("Holding was not found in the mock dataset.");
  }

  holding.profile = profile;
  dashboard.logs = [
    createLog("info", "holdings-ui", `${holding.symbol} moved to Profile ${profile} with optimistic UI.`),
    ...dashboard.logs
  ].slice(0, 16);
  dashboard.asOf = new Date().toISOString();
  writeCache(dashboard);
  return holding;
}

export function getStoredAdminKey(): string {
  return localStorage.getItem(ADMIN_KEY) || "";
}

export function setStoredAdminKey(value: string) {
  localStorage.setItem(ADMIN_KEY, value);
}

export function clearDemoCache() {
  localStorage.removeItem(CACHE_KEY);
}

export function createLog(level: OpsLog["level"], source: string, message: string): OpsLog {
  return {
    id: `LOG-${Date.now()}`,
    level,
    source,
    message,
    timestamp: new Date().toLocaleTimeString("en-US", { hour12: false })
  };
}
