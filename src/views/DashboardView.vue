<template>
  <main class="app-shell">
    <aside class="sidebar" :aria-label="t.navigationLabel">
      <div class="brand">
        <div class="brand-mark">TO</div>
        <div>
          <strong>{{ t.brandTitle }}</strong>
          <span>{{ t.brandSubtitle }}</span>
        </div>
      </div>

      <nav>
        <a href="#accounts">{{ t.navAccounts }}</a>
        <a href="#holdings">{{ t.navHoldings }}</a>
        <a href="#strategy">{{ t.navProfiles }}</a>
        <a href="#logs">{{ t.navLogs }}</a>
      </nav>

      <div class="admin-card">
        <label for="admin-key">{{ t.adminKey }}</label>
        <div class="admin-input">
          <input
            id="admin-key"
            :value="store.adminKey"
            type="password"
            :placeholder="t.adminPlaceholder"
            @input="store.saveAdminKey(($event.target as HTMLInputElement).value)"
          />
          <span :class="{ ready: store.hasAdminKey }">{{ store.hasAdminKey ? t.set : t.empty }}</span>
        </div>
      </div>
    </aside>

    <section class="workspace">
      <header class="topbar">
        <div>
          <div class="topbar-meta">
            <p class="eyebrow">Vue 3 + TypeScript + Pinia</p>
            <div class="language-toggle" :aria-label="t.language">
              <button
                v-for="option in languageOptions"
                :key="option.locale"
                :class="{ selected: locale === option.locale }"
                type="button"
                @click="locale = option.locale"
              >
                <span class="flag" aria-hidden="true">{{ option.flag }}</span>
                <span>{{ option.label }}</span>
              </button>
            </div>
          </div>
          <h1>{{ t.title }}</h1>
          <p>{{ t.heroCopy }}</p>
        </div>
        <div class="topbar-actions">
          <span class="snapshot">{{ t.snapshot }} {{ snapshotTime }}</span>
          <button class="secondary-button" @click="store.resetDemo">{{ t.resetCache }}</button>
          <button class="primary-button" @click="store.loadDashboard">{{ t.refresh }}</button>
        </div>
      </header>

      <section v-if="store.loadState === 'loading'" class="state-panel">{{ t.loading }}</section>
      <section v-else-if="store.loadState === 'error'" class="state-panel error">{{ store.error }}</section>

      <section class="kpi-grid" :aria-label="t.portfolioSummary">
        <article class="metric">
          <span>{{ t.totalEquity }}</span>
          <strong>{{ money(store.totalEquity) }}</strong>
          <small>{{ t.supervisedAccounts(store.accounts.length) }}</small>
        </article>
        <article class="metric">
          <span>{{ t.availableCash }}</span>
          <strong>{{ money(store.totalCash) }}</strong>
          <small>{{ t.cashRatio(cashRatio) }}</small>
        </article>
        <article class="metric">
          <span>{{ t.dailyPnl }}</span>
          <strong :class="pnlClass(store.totalPnl)">{{ signedMoney(store.totalPnl) }}</strong>
          <small>{{ t.mockPositions }}</small>
        </article>
        <article class="metric">
          <span>{{ t.openTickets }}</span>
          <strong>{{ store.openTickets }}</strong>
          <small>{{ t.reviewQueue }}</small>
        </article>
      </section>

      <section class="server-grid" :aria-label="t.serverStatus">
        <article v-for="server in store.servers" :key="server.id" class="server-card">
          <div>
            <span :class="['status-dot', server.status.toLowerCase()]"></span>
            <strong>{{ server.name }}</strong>
            <small>{{ server.region }}</small>
          </div>
          <dl>
            <div>
              <dt>{{ t.latency }}</dt>
              <dd>{{ server.latencyMs }} ms</dd>
            </div>
            <div>
              <dt>{{ t.queue }}</dt>
              <dd>{{ server.queueDepth }}</dd>
            </div>
            <div>
              <dt>{{ t.heartbeat }}</dt>
              <dd>{{ server.lastHeartbeat }}</dd>
            </div>
          </dl>
        </article>
      </section>

      <section class="content-grid" id="accounts">
        <article class="panel">
          <div class="panel-head">
            <div>
              <p class="eyebrow">{{ t.multiAccount }}</p>
              <h2>{{ t.accounts }}</h2>
            </div>
            <div class="filter-row">
              <select v-model="store.accountStatus" :aria-label="t.accountStatus">
                <option value="All">{{ t.allStatuses }}</option>
                <option value="Active">{{ t.active }}</option>
                <option value="Review">{{ t.review }}</option>
                <option value="Paused">{{ t.paused }}</option>
              </select>
              <select v-model="store.riskLevel" :aria-label="t.riskLevel">
                <option value="All">{{ t.allRiskLevels }}</option>
                <option value="Low">{{ t.low }}</option>
                <option value="Medium">{{ t.medium }}</option>
                <option value="High">{{ t.high }}</option>
              </select>
            </div>
          </div>

          <div v-if="store.filteredAccounts.length === 0" class="empty-state">
            {{ t.noAccounts }}
          </div>
          <div v-else class="account-list">
            <article v-for="account in store.filteredAccounts" :key="account.id" class="account-row">
              <div>
                <strong>{{ account.name }}</strong>
                <small>{{ account.id }} / {{ account.desk }}</small>
              </div>
              <span :class="['pill', account.status.toLowerCase()]">{{ accountStatusLabel(account.status) }}</span>
              <span class="number">{{ money(account.equity) }}</span>
              <span :class="['risk', account.riskLevel.toLowerCase()]">{{ riskLevelLabel(account.riskLevel) }}</span>
            </article>
          </div>
        </article>

        <article class="panel">
          <div class="panel-head">
            <div>
              <p class="eyebrow">{{ t.groupedBySymbol }}</p>
              <h2>{{ t.exposureRollup }}</h2>
            </div>
          </div>
          <div class="rollup-list">
            <article v-for="holding in store.groupedHoldings" :key="holding.symbol" class="rollup-row">
              <div>
                <strong>{{ holding.symbol }}</strong>
                <small>{{ holding.name }} / {{ t.accountCount(holding.accounts) }}</small>
              </div>
              <span>{{ money(holding.exposure) }}</span>
              <span :class="pnlClass(holding.dayPnl)">{{ signedMoney(holding.dayPnl) }}</span>
            </article>
          </div>
        </article>
      </section>

      <section class="panel" id="holdings">
        <div class="panel-head">
          <div>
            <p class="eyebrow">{{ t.holdingsEyebrow }}</p>
            <h2>{{ t.portfolioHoldings }}</h2>
          </div>
          <div class="filter-row wide">
            <input v-model="store.holdingQuery" type="search" :placeholder="t.holdingSearch" />
            <select v-model="store.selectedAccountId" :aria-label="t.holdingAccountFilter">
              <option value="All">{{ t.allAccounts }}</option>
              <option v-for="account in store.accounts" :key="account.id" :value="account.id">
                {{ account.name }}
              </option>
            </select>
            <select v-model="store.selectedProfile" :aria-label="t.profileFilter">
              <option value="All">{{ t.allProfiles }}</option>
              <option value="A">{{ t.profileA }}</option>
              <option value="B">{{ t.profileB }}</option>
            </select>
          </div>
        </div>

        <p v-if="store.optimisticMessage" class="inline-notice">{{ store.optimisticMessage }}</p>

        <div class="table-wrap">
          <table>
            <thead>
              <tr>
                <th><button @click="store.setSort('symbol')">{{ t.symbol }} {{ sortMark("symbol") }}</button></th>
                <th>{{ t.account }}</th>
                <th><button @click="store.setSort('market')">{{ t.market }} {{ sortMark("market") }}</button></th>
                <th><button @click="store.setSort('quantity')">{{ t.qty }} {{ sortMark("quantity") }}</button></th>
                <th>{{ t.last }}</th>
                <th><button @click="store.setSort('exposure')">{{ t.exposure }} {{ sortMark("exposure") }}</button></th>
                <th><button @click="store.setSort('dayPnl')">{{ t.dayPnl }} {{ sortMark("dayPnl") }}</button></th>
                <th><button @click="store.setSort('profile')">{{ t.profile }} {{ sortMark("profile") }}</button></th>
              </tr>
            </thead>
            <tbody>
              <tr v-if="store.filteredHoldings.length === 0">
                <td colspan="8" class="empty-cell">{{ t.noHoldings }}</td>
              </tr>
              <tr v-for="holding in store.filteredHoldings" :key="holding.id">
                <td>
                  <strong>{{ holding.symbol }}</strong>
                  <small>{{ holding.name }}</small>
                </td>
                <td>{{ accountName(holding.accountId) }}</td>
                <td>{{ holding.market }}</td>
                <td>{{ integer(holding.quantity) }}</td>
                <td>{{ price(holding.last) }}</td>
                <td>{{ money(holding.exposure) }}</td>
                <td :class="pnlClass(holding.dayPnl)">{{ signedMoney(holding.dayPnl) }}</td>
                <td>
                  <select
                    :value="holding.profile"
                    :aria-label="t.moveHoldingProfile"
                    @change="store.moveHoldingToProfile(holding, ($event.target as HTMLSelectElement).value as ProfileVariant)"
                  >
                    <option value="A">A</option>
                    <option value="B">B</option>
                  </select>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </section>

      <section class="content-grid" id="strategy">
        <article class="panel">
          <div class="panel-head">
            <div>
              <p class="eyebrow">{{ t.strategyModal }}</p>
              <h2>{{ t.abProfileConfig }}</h2>
            </div>
          </div>
          <div class="profile-list">
            <article v-for="profile in store.strategies" :key="profile.id" class="profile-card">
              <div>
                <strong>{{ profile.label }}</strong>
                <small>{{ t.maxExposure }}: {{ profile.maxSingleNameExposure }}%</small>
                <small>{{ t.window }}: {{ profile.rebalanceWindow }}</small>
              </div>
              <button class="secondary-button" @click="openProfile(profile)">{{ t.configure }}</button>
            </article>
          </div>
        </article>

        <article class="panel" id="logs">
          <div class="panel-head">
            <div>
              <p class="eyebrow">{{ t.mockRealtime }}</p>
              <h2>{{ t.operationsLog }}</h2>
            </div>
            <button class="secondary-button" @click="addMockLog">{{ t.addLog }}</button>
          </div>
          <div class="log-viewer" aria-live="polite">
            <article v-for="log in store.filteredLogs" :key="log.id" :class="['log-row', log.level]">
              <time>{{ log.timestamp }}</time>
              <strong>{{ log.source }}</strong>
              <span>{{ log.message }}</span>
            </article>
          </div>
        </article>
      </section>
    </section>

    <div v-if="editingProfile" class="modal-backdrop" role="presentation" @click.self="editingProfile = null">
      <form class="modal" @submit.prevent="saveEditingProfile">
        <div class="panel-head">
          <div>
            <p class="eyebrow">{{ t.profile }} {{ editingProfile.variant }}</p>
            <h2>{{ editingProfile.label }}</h2>
          </div>
          <button class="icon-button" type="button" :aria-label="t.closeModal" @click="editingProfile = null">x</button>
        </div>

        <label>
          <span>{{ t.maxExposure }}</span>
          <input v-model.number="editingProfile.maxSingleNameExposure" min="1" max="50" type="number" />
        </label>
        <label>
          <span>{{ t.reviewWindow }}</span>
          <input v-model="editingProfile.rebalanceWindow" type="text" />
        </label>
        <label class="checkbox-row">
          <input v-model="editingProfile.alertsEnabled" type="checkbox" />
          <span>{{ t.enableAlerts }}</span>
        </label>
        <label>
          <span>{{ t.demoNotes }}</span>
          <textarea v-model="editingProfile.notes" rows="4"></textarea>
        </label>

        <div class="modal-actions">
          <button class="secondary-button" type="button" @click="editingProfile = null">{{ t.cancel }}</button>
          <button class="primary-button" type="submit">{{ t.saveProfile }}</button>
        </div>
      </form>
    </div>
  </main>
</template>

<script setup lang="ts">
import { computed, onMounted, onUnmounted, ref } from "vue";
import { useDashboardStore } from "../stores/dashboard";
import type { AccountStatus, Holding, ProfileVariant, RiskLevel, StrategyProfile } from "../data";

type Locale = "en" | "zhHans" | "zhHant";

const languageOptions: { locale: Locale; flag: string; label: string }[] = [
  { locale: "en", flag: "🇬🇧", label: "English" },
  { locale: "zhHans", flag: "🇨🇳", label: "简体中文" },
  { locale: "zhHant", flag: "🇹🇼", label: "繁體中文" }
];

const dictionaries = {
  en: {
    navigationLabel: "Dashboard navigation",
    brandTitle: "Trading Operations",
    brandSubtitle: "Sanitized portfolio demo",
    navAccounts: "Accounts",
    navHoldings: "Holdings",
    navProfiles: "Profiles",
    navLogs: "Logs",
    adminKey: "Demo admin key",
    adminPlaceholder: "Stored locally",
    set: "Set",
    empty: "Empty",
    language: "Language",
    title: "Trading Operations Dashboard",
    heroCopy:
      "A frontend-focused full-stack demo for monitoring mock multi-account portfolio operations, status checks, profile settings, and sanitized activity logs.",
    snapshot: "Snapshot",
    resetCache: "Reset cache",
    refresh: "Refresh",
    loading: "Loading sanitized mock data...",
    portfolioSummary: "Portfolio summary",
    totalEquity: "Total equity",
    availableCash: "Available cash",
    dailyPnl: "Daily P&L",
    openTickets: "Open tickets",
    supervisedAccounts: (count: number) => `${count} supervised demo accounts`,
    cashRatio: (ratio: number) => `${ratio}% of total equity`,
    mockPositions: "Mock marked positions only",
    reviewQueue: "Operational review queue",
    serverStatus: "Server status",
    latency: "Latency",
    queue: "Queue",
    heartbeat: "Heartbeat",
    multiAccount: "Multi-account dashboard",
    accounts: "Accounts",
    accountStatus: "Account status",
    allStatuses: "All statuses",
    riskLevel: "Risk level",
    allRiskLevels: "All risk levels",
    active: "Active",
    review: "Review",
    paused: "Paused",
    low: "Low",
    medium: "Medium",
    high: "High",
    noAccounts: "No accounts match the current filters.",
    groupedBySymbol: "Grouped by symbol",
    exposureRollup: "Exposure Rollup",
    accountCount: (count: number) => `${count} accounts`,
    holdingsEyebrow: "Sorting, filtering, optimistic updates",
    portfolioHoldings: "Portfolio Holdings",
    holdingSearch: "Filter symbol, name, or market",
    holdingAccountFilter: "Holding account filter",
    allAccounts: "All accounts",
    profileFilter: "Profile filter",
    allProfiles: "All profiles",
    profileA: "Profile A",
    profileB: "Profile B",
    symbol: "Symbol",
    account: "Account",
    market: "Market",
    qty: "Qty",
    last: "Last",
    exposure: "Exposure",
    dayPnl: "Day P&L",
    profile: "Profile",
    noHoldings: "No holdings match the filters.",
    moveHoldingProfile: "Move holding to profile",
    strategyModal: "Strategy configuration modal",
    abProfileConfig: "A/B Profile Configuration",
    maxExposure: "Max single-name exposure",
    window: "Window",
    configure: "Configure",
    mockRealtime: "Mock real-time stream",
    operationsLog: "Operations Log",
    addLog: "Add log",
    closeModal: "Close modal",
    reviewWindow: "Review window",
    enableAlerts: "Enable review alerts",
    demoNotes: "Demo notes",
    cancel: "Cancel",
    saveProfile: "Save profile",
    mockHeartbeat: "Simulated heartbeat received from local mock service.",
    mockReviewItem: "Manual review item added to the sanitized demo log."
  },
  zhHans: {
    navigationLabel: "仪表盘导航",
    brandTitle: "交易运营",
    brandSubtitle: "脱敏作品集演示",
    navAccounts: "账户",
    navHoldings: "持仓",
    navProfiles: "配置",
    navLogs: "日志",
    adminKey: "演示管理员密钥",
    adminPlaceholder: "仅本地存储",
    set: "已设置",
    empty: "未填写",
    language: "语言",
    title: "交易运营仪表盘",
    heroCopy: "一个以前端为重点的全栈演示，用于监控模拟多账户组合运营、状态检查、配置档案和脱敏活动日志。",
    snapshot: "快照",
    resetCache: "重置缓存",
    refresh: "刷新",
    loading: "正在加载脱敏模拟数据...",
    portfolioSummary: "组合概览",
    totalEquity: "总权益",
    availableCash: "可用现金",
    dailyPnl: "当日盈亏",
    openTickets: "待处理事项",
    supervisedAccounts: (count: number) => `${count} 个受监控演示账户`,
    cashRatio: (ratio: number) => `占总权益 ${ratio}%`,
    mockPositions: "仅使用模拟盯市持仓",
    reviewQueue: "运营复核队列",
    serverStatus: "服务状态",
    latency: "延迟",
    queue: "队列",
    heartbeat: "心跳",
    multiAccount: "多账户仪表盘",
    accounts: "账户",
    accountStatus: "账户状态",
    allStatuses: "全部状态",
    riskLevel: "风险等级",
    allRiskLevels: "全部风险等级",
    active: "运行中",
    review: "复核",
    paused: "暂停",
    low: "低",
    medium: "中",
    high: "高",
    noAccounts: "没有账户符合当前筛选条件。",
    groupedBySymbol: "按标的汇总",
    exposureRollup: "敞口汇总",
    accountCount: (count: number) => `${count} 个账户`,
    holdingsEyebrow: "排序、筛选、乐观更新",
    portfolioHoldings: "组合持仓",
    holdingSearch: "筛选代码、名称或市场",
    holdingAccountFilter: "持仓账户筛选",
    allAccounts: "全部账户",
    profileFilter: "配置筛选",
    allProfiles: "全部配置",
    profileA: "配置 A",
    profileB: "配置 B",
    symbol: "代码",
    account: "账户",
    market: "市场",
    qty: "数量",
    last: "最新价",
    exposure: "敞口",
    dayPnl: "当日盈亏",
    profile: "配置",
    noHoldings: "没有持仓符合当前筛选条件。",
    moveHoldingProfile: "移动持仓到配置",
    strategyModal: "策略配置弹窗",
    abProfileConfig: "A/B 配置界面",
    maxExposure: "单一标的最大敞口",
    window: "窗口",
    configure: "配置",
    mockRealtime: "模拟实时流",
    operationsLog: "运营日志",
    addLog: "添加日志",
    closeModal: "关闭弹窗",
    reviewWindow: "复核窗口",
    enableAlerts: "启用复核提醒",
    demoNotes: "演示备注",
    cancel: "取消",
    saveProfile: "保存配置",
    mockHeartbeat: "已收到本地模拟服务的心跳。",
    mockReviewItem: "已向脱敏演示日志添加人工复核事项。"
  },
  zhHant: {
    navigationLabel: "儀表板導覽",
    brandTitle: "交易營運",
    brandSubtitle: "脫敏作品集展示",
    navAccounts: "帳戶",
    navHoldings: "持倉",
    navProfiles: "配置",
    navLogs: "日誌",
    adminKey: "展示管理員金鑰",
    adminPlaceholder: "僅本機儲存",
    set: "已設定",
    empty: "未填寫",
    language: "語言",
    title: "交易營運儀表板",
    heroCopy: "一個以前端為重點的全端展示，用於監控模擬多帳戶投資組合營運、狀態檢查、配置檔案與脫敏活動日誌。",
    snapshot: "快照",
    resetCache: "重置快取",
    refresh: "重新整理",
    loading: "正在載入脫敏模擬資料...",
    portfolioSummary: "組合概覽",
    totalEquity: "總權益",
    availableCash: "可用現金",
    dailyPnl: "當日損益",
    openTickets: "待處理事項",
    supervisedAccounts: (count: number) => `${count} 個受監控展示帳戶`,
    cashRatio: (ratio: number) => `占總權益 ${ratio}%`,
    mockPositions: "僅使用模擬盯市持倉",
    reviewQueue: "營運覆核佇列",
    serverStatus: "服務狀態",
    latency: "延遲",
    queue: "佇列",
    heartbeat: "心跳",
    multiAccount: "多帳戶儀表板",
    accounts: "帳戶",
    accountStatus: "帳戶狀態",
    allStatuses: "全部狀態",
    riskLevel: "風險等級",
    allRiskLevels: "全部風險等級",
    active: "運行中",
    review: "覆核",
    paused: "暫停",
    low: "低",
    medium: "中",
    high: "高",
    noAccounts: "沒有帳戶符合目前篩選條件。",
    groupedBySymbol: "按標的彙總",
    exposureRollup: "曝險彙總",
    accountCount: (count: number) => `${count} 個帳戶`,
    holdingsEyebrow: "排序、篩選、樂觀更新",
    portfolioHoldings: "組合持倉",
    holdingSearch: "篩選代碼、名稱或市場",
    holdingAccountFilter: "持倉帳戶篩選",
    allAccounts: "全部帳戶",
    profileFilter: "配置篩選",
    allProfiles: "全部配置",
    profileA: "配置 A",
    profileB: "配置 B",
    symbol: "代碼",
    account: "帳戶",
    market: "市場",
    qty: "數量",
    last: "最新價",
    exposure: "曝險",
    dayPnl: "當日損益",
    profile: "配置",
    noHoldings: "沒有持倉符合目前篩選條件。",
    moveHoldingProfile: "移動持倉到配置",
    strategyModal: "策略配置彈窗",
    abProfileConfig: "A/B 配置介面",
    maxExposure: "單一標的最大曝險",
    window: "視窗",
    configure: "配置",
    mockRealtime: "模擬即時串流",
    operationsLog: "營運日誌",
    addLog: "新增日誌",
    closeModal: "關閉彈窗",
    reviewWindow: "覆核視窗",
    enableAlerts: "啟用覆核提醒",
    demoNotes: "展示備註",
    cancel: "取消",
    saveProfile: "儲存配置",
    mockHeartbeat: "已收到本機模擬服務的心跳。",
    mockReviewItem: "已向脫敏展示日誌新增人工覆核事項。"
  }
} as const;

const store = useDashboardStore();
const locale = ref<Locale>("en");
const editingProfile = ref<StrategyProfile | null>(null);
let logTimer: number | undefined;

const t = computed(() => dictionaries[locale.value]);

const snapshotTime = computed(() => {
  const timeLocale = locale.value === "en" ? "en-GB" : locale.value === "zhHans" ? "zh-CN" : "zh-TW";
  return new Date(store.asOf).toLocaleTimeString(timeLocale, { hour12: false });
});

const cashRatio = computed(() => {
  if (!store.totalEquity) return 0;
  return Math.round((store.totalCash / store.totalEquity) * 100);
});

onMounted(() => {
  store.loadDashboard();
  logTimer = window.setInterval(() => {
    store.pushLog("info", "mock-feed", t.value.mockHeartbeat);
  }, 12000);
});

onUnmounted(() => {
  if (logTimer) window.clearInterval(logTimer);
});

function openProfile(profile: StrategyProfile) {
  editingProfile.value = { ...profile };
}

function saveEditingProfile() {
  if (!editingProfile.value) return;
  store.saveProfile({ ...editingProfile.value });
  editingProfile.value = null;
}

function addMockLog() {
  store.pushLog("warning", "review-queue", t.value.mockReviewItem);
}

function accountName(accountId: Holding["accountId"]) {
  return store.accounts.find((account) => account.id === accountId)?.name || accountId;
}

function accountStatusLabel(status: AccountStatus) {
  const labels = {
    Active: t.value.active,
    Review: t.value.review,
    Paused: t.value.paused
  };
  return labels[status];
}

function riskLevelLabel(level: RiskLevel) {
  const labels = {
    Low: t.value.low,
    Medium: t.value.medium,
    High: t.value.high
  };
  return labels[level];
}

function money(value: number) {
  return new Intl.NumberFormat("en-US", {
    style: "currency",
    currency: "USD",
    maximumFractionDigits: 0
  }).format(value);
}

function signedMoney(value: number) {
  const formatted = money(Math.abs(value));
  if (value > 0) return `+${formatted}`;
  if (value < 0) return `-${formatted}`;
  return formatted;
}

function integer(value: number) {
  return new Intl.NumberFormat("en-US", { maximumFractionDigits: 0 }).format(value);
}

function price(value: number) {
  return new Intl.NumberFormat("en-US", {
    minimumFractionDigits: 2,
    maximumFractionDigits: 2
  }).format(value);
}

function pnlClass(value: number) {
  if (value > 0) return "positive";
  if (value < 0) return "negative";
  return "";
}

function sortMark(key: string) {
  if (store.sortKey !== key) return "";
  return store.sortDirection === "asc" ? "^" : "v";
}
</script>
