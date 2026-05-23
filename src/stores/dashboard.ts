import { defineStore } from "pinia";
import { computed, ref } from "vue";
import {
  clearDemoCache,
  fetchMockDashboard,
  fetchBackendRpaJobs,
  getStoredAdminKey,
  saveStrategyProfile,
  setStoredAdminKey,
  submitBackendRpaJob,
  updateHoldingProfile
} from "../api";
import {
  fallbackDashboard,
  type AccountStatus,
  type GroupedHolding,
  type Holding,
  type LogLevel,
  type ProfileVariant,
  type RiskLevel,
  type RpaAction,
  type RpaJob,
  type SortDirection,
  type StrategyProfile
} from "../data";

type HoldingSortKey = "symbol" | "market" | "quantity" | "exposure" | "dayPnl" | "profile";
type LoadState = "idle" | "loading" | "ready" | "error";

export const useDashboardStore = defineStore("dashboard", () => {
  const loadState = ref<LoadState>("idle");
  const error = ref("");
  const asOf = ref(fallbackDashboard.asOf);
  const accounts = ref([...fallbackDashboard.accounts]);
  const holdings = ref([...fallbackDashboard.holdings]);
  const strategies = ref(fallbackDashboard.strategies.map((item) => ({ ...item })));
  const logs = ref([...fallbackDashboard.logs]);
  const servers = ref([...fallbackDashboard.servers]);
  const rpaJobs = ref<RpaJob[]>([...(fallbackDashboard.rpaJobs || [])]);
  const rpaOnline = ref(false);
  const rpaBusy = ref(false);
  const selectedRpaAccountId = ref(fallbackDashboard.accounts[0].id);
  const selectedRpaAction = ref<RpaAction>("refresh_holdings");
  const accountStatus = ref<"All" | AccountStatus>("All");
  const riskLevel = ref<"All" | RiskLevel>("All");
  const holdingQuery = ref("");
  const selectedAccountId = ref("All");
  const selectedProfile = ref<"All" | ProfileVariant>("All");
  const sortKey = ref<HoldingSortKey>("exposure");
  const sortDirection = ref<SortDirection>("desc");
  const adminKey = ref(getStoredAdminKey());
  const optimisticMessage = ref("");

  const filteredAccounts = computed(() => {
    return accounts.value.filter((account) => {
      const statusMatch = accountStatus.value === "All" || account.status === accountStatus.value;
      const riskMatch = riskLevel.value === "All" || account.riskLevel === riskLevel.value;
      return statusMatch && riskMatch;
    });
  });

  const totalEquity = computed(() => accounts.value.reduce((sum, account) => sum + account.equity, 0));
  const totalCash = computed(() => accounts.value.reduce((sum, account) => sum + account.cash, 0));
  const totalPnl = computed(() => accounts.value.reduce((sum, account) => sum + account.dailyPnl, 0));
  const openTickets = computed(() => accounts.value.reduce((sum, account) => sum + account.activeTickets, 0));

  const filteredHoldings = computed(() => {
    const query = holdingQuery.value.trim().toLowerCase();
    const rows = holdings.value.filter((holding) => {
      const queryMatch =
        !query ||
        holding.symbol.toLowerCase().includes(query) ||
        holding.name.toLowerCase().includes(query) ||
        holding.market.toLowerCase().includes(query);
      const accountMatch = selectedAccountId.value === "All" || holding.accountId === selectedAccountId.value;
      const profileMatch = selectedProfile.value === "All" || holding.profile === selectedProfile.value;
      return queryMatch && accountMatch && profileMatch;
    });

    return [...rows].sort((a, b) => {
      const aValue = a[sortKey.value];
      const bValue = b[sortKey.value];
      const modifier = sortDirection.value === "asc" ? 1 : -1;
      if (typeof aValue === "number" && typeof bValue === "number") {
        return (aValue - bValue) * modifier;
      }
      return String(aValue).localeCompare(String(bValue)) * modifier;
    });
  });

  const groupedHoldings = computed<GroupedHolding[]>(() => {
    const groups = new Map<string, GroupedHolding>();
    holdings.value.forEach((holding) => {
      const existing = groups.get(holding.symbol);
      if (!existing) {
        groups.set(holding.symbol, {
          symbol: holding.symbol,
          name: holding.name,
          market: holding.market,
          accounts: 1,
          quantity: holding.quantity,
          exposure: holding.exposure,
          dayPnl: holding.dayPnl,
          profiles: [holding.profile]
        });
        return;
      }

      existing.accounts += 1;
      existing.quantity += holding.quantity;
      existing.exposure += holding.exposure;
      existing.dayPnl += holding.dayPnl;
      if (!existing.profiles.includes(holding.profile)) existing.profiles.push(holding.profile);
    });
    return [...groups.values()].sort((a, b) => b.exposure - a.exposure);
  });

  const filteredLogs = computed(() => logs.value);
  const hasAdminKey = computed(() => adminKey.value.trim().length > 0);

  async function loadDashboard() {
    loadState.value = "loading";
    error.value = "";
    try {
      const payload = await fetchMockDashboard();
      asOf.value = payload.asOf;
      accounts.value = payload.accounts;
      holdings.value = payload.holdings;
      strategies.value = payload.strategies.map((item) => ({ ...item }));
      logs.value = payload.logs;
      servers.value = payload.servers;
      rpaJobs.value = payload.rpaJobs || rpaJobs.value;
      loadState.value = "ready";
      await refreshRpaJobs();
    } catch (reason) {
      error.value = reason instanceof Error ? reason.message : "Unable to load mock dashboard data.";
      loadState.value = "error";
    }
  }

  async function refreshRpaJobs() {
    try {
      rpaJobs.value = await fetchBackendRpaJobs();
      rpaOnline.value = true;
    } catch {
      rpaOnline.value = false;
    }
  }

  function setSort(nextKey: HoldingSortKey) {
    if (sortKey.value === nextKey) {
      sortDirection.value = sortDirection.value === "asc" ? "desc" : "asc";
      return;
    }
    sortKey.value = nextKey;
    sortDirection.value = nextKey === "symbol" || nextKey === "market" ? "asc" : "desc";
  }

  async function saveProfile(profile: StrategyProfile) {
    const previous = strategies.value.map((item) => ({ ...item }));
    strategies.value = strategies.value.map((item) => (item.id === profile.id ? { ...profile } : item));
    optimisticMessage.value = `${profile.label} saved locally while the mock service confirms.`;

    try {
      await saveStrategyProfile(profile);
      logs.value = [
        {
          id: `LOG-${Date.now()}`,
          level: "info",
          source: "strategy-ui",
          message: `${profile.label} confirmed by mock service.`,
          timestamp: new Date().toLocaleTimeString("en-US", { hour12: false })
        },
        ...logs.value
      ];
    } catch {
      strategies.value = previous;
      optimisticMessage.value = "Profile update was rolled back after a mock service error.";
    }
  }

  async function moveHoldingToProfile(holding: Holding, profile: ProfileVariant) {
    const previousProfile = holding.profile;
    holding.profile = profile;
    optimisticMessage.value = `${holding.symbol} moved to Profile ${profile} before mock confirmation.`;

    try {
      await updateHoldingProfile(holding.id, profile);
    } catch {
      holding.profile = previousProfile;
      optimisticMessage.value = `${holding.symbol} profile change was rolled back.`;
    }
  }

  async function submitRpaJob() {
    rpaBusy.value = true;
    try {
      const job = await submitBackendRpaJob(selectedRpaAccountId.value, selectedRpaAction.value);
      rpaJobs.value = [job, ...rpaJobs.value.filter((item) => item.id !== job.id)];
      rpaOnline.value = true;
      pushLog("info", "rpa-worker", `${job.id} accepted by backend mock RPA queue.`);
    } catch {
      rpaOnline.value = false;
      pushLog("warning", "rpa-worker", "Backend mock RPA API is offline. Start the Python backend to run jobs.");
    } finally {
      rpaBusy.value = false;
    }
  }

  function saveAdminKey(value: string) {
    adminKey.value = value;
    setStoredAdminKey(value);
  }

  function resetDemo() {
    clearDemoCache();
    adminKey.value = "";
    setStoredAdminKey("");
    optimisticMessage.value = "";
    loadDashboard();
  }

  function pushLog(level: LogLevel, source: string, message: string) {
    logs.value = [
      {
        id: `LOG-${Date.now()}`,
        level,
        source,
        message,
        timestamp: new Date().toLocaleTimeString("en-US", { hour12: false })
      },
      ...logs.value
    ].slice(0, 20);
  }

  return {
    accountStatus,
    accounts,
    adminKey,
    asOf,
    error,
    filteredAccounts,
    filteredHoldings,
    filteredLogs,
    groupedHoldings,
    hasAdminKey,
    holdingQuery,
    holdings,
    loadDashboard,
    loadState,
    logs,
    moveHoldingToProfile,
    openTickets,
    optimisticMessage,
    pushLog,
    resetDemo,
    riskLevel,
    refreshRpaJobs,
    rpaBusy,
    rpaJobs,
    rpaOnline,
    saveAdminKey,
    saveProfile,
    selectedRpaAccountId,
    selectedRpaAction,
    submitRpaJob,
    selectedAccountId,
    selectedProfile,
    servers,
    setSort,
    sortDirection,
    sortKey,
    strategies,
    totalCash,
    totalEquity,
    totalPnl
  };
});
