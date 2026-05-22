<template>
  <main class="shell">
    <aside class="sidebar" aria-label="Workspace navigation">
      <div class="brand">
        <div class="brand-mark">TD</div>
        <div>
          <strong>{{ t.brandTitle }}</strong>
          <span>{{ t.brandSubtitle }}</span>
        </div>
      </div>

      <nav>
        <a class="active" href="#overview">{{ t.navOverview }}</a>
        <a href="#accounts">{{ t.navAccounts }}</a>
        <a href="#risk">{{ t.navRisk }}</a>
        <a href="#execution">{{ t.navExecution }}</a>
        <a href="#rpa">RPA</a>
      </nav>

      <div class="sidebar-footer">
        <span>{{ dataSourceLabel }}</span>
        <strong>Vue + TypeScript + Python</strong>
      </div>
    </aside>

    <section class="workspace">
      <header class="hero" id="overview">
        <div>
          <div class="hero-tools">
            <p class="eyebrow">{{ t.portfolioProject }}</p>
            <div class="language-toggle" role="group" :aria-label="t.language">
              <button :class="{ selected: locale === 'en' }" @click="locale = 'en'">
                <span class="flag flag-sg" aria-hidden="true"></span>
                EN
              </button>
              <button :class="{ selected: locale === 'zh' }" @click="locale = 'zh'">
                <span class="flag flag-cn" aria-hidden="true"></span>
                简体
              </button>
              <button :class="{ selected: locale === 'zhHant' }" @click="locale = 'zhHant'">
                <span class="flag flag-tw" aria-hidden="true"></span>
                繁體
              </button>
            </div>
          </div>
          <h1>{{ t.title }}</h1>
          <p class="hero-copy">{{ t.heroCopy }}</p>
        </div>
        <div class="market-clock">
          <span>{{ t.singaporeSession }}</span>
          <strong>{{ clock }}</strong>
          <small>SGT · {{ asOfLabel }}</small>
        </div>
      </header>

      <section class="kpi-grid" :aria-label="t.metrics">
        <article class="metric">
          <span>{{ t.totalEquity }}</span>
          <strong>{{ money(totalEquity) }}</strong>
          <small>{{ t.acrossAccounts(accounts.length) }}</small>
        </article>
        <article class="metric">
          <span>{{ t.availableCash }}</span>
          <strong>{{ money(totalCash) }}</strong>
          <small>{{ t.cashRatio(cashRatio) }}</small>
        </article>
        <article class="metric">
          <span>{{ t.dailyPnl }}</span>
          <strong :class="pnlClass(totalPnl)">{{ signedMoney(totalPnl) }}</strong>
          <small>{{ t.pnlHint }}</small>
        </article>
        <article class="metric">
          <span>{{ t.activeOrders }}</span>
          <strong>{{ activeOrders }}</strong>
          <small>{{ t.riskItems(highRiskCount) }}</small>
        </article>
      </section>

      <section class="content-grid">
        <article class="panel rpa-panel" id="rpa">
          <div class="panel-head">
            <div>
              <p class="eyebrow">{{ rpaCopy.eyebrow }}</p>
              <h2>{{ rpaCopy.title }}</h2>
            </div>
            <span class="count-badge">{{ rpaCommands.length }}</span>
          </div>

          <div class="rpa-command-bar">
            <label>
              <span>{{ rpaCopy.account }}</span>
              <select v-model="selectedRpaAccountId">
                <option v-for="account in allAccounts" :key="account.id" :value="account.id">
                  {{ account.name }} · {{ account.id }}
                </option>
              </select>
            </label>
            <label>
              <span>{{ rpaCopy.action }}</span>
              <select v-model="selectedRpaAction">
                <option v-for="action in rpaActions" :key="action" :value="action">
                  {{ rpaActionLabel(action) }}
                </option>
              </select>
            </label>
            <button class="btn-primary-action" :disabled="rpaBusy" @click="runRpaCommand">
              {{ rpaBusy ? rpaCopy.running : rpaCopy.run }}
            </button>
          </div>

          <p class="api-note">{{ rpaCopy.note }}</p>
          <p v-if="rpaMessage" class="rpa-message">{{ rpaMessage }}</p>
        </article>

        <article class="panel rpa-log-panel">
          <div class="panel-head">
            <div>
              <p class="eyebrow">{{ rpaCopy.auditEyebrow }}</p>
              <h2>{{ rpaCopy.auditTitle }}</h2>
            </div>
          </div>

          <div class="rpa-log">
            <article v-for="command in rpaCommands" :key="command.id" class="rpa-command">
              <div>
                <strong>{{ command.id }} · {{ rpaActionLabel(command.action) }}</strong>
                <span>{{ command.accountId }} · {{ command.createdAt }} · {{ command.operator }}</span>
              </div>
              <span :class="['rpa-status', command.status.toLowerCase()]">
                {{ rpaStatusLabel(command.status) }}
              </span>
              <p>{{ rpaMessageLabel(command) }}</p>
              <div class="rpa-progress" :aria-label="`${command.progress}%`">
                <span :style="{ width: `${command.progress}%` }"></span>
              </div>
              <small class="rpa-current-step">{{ rpaStepLabel(command.currentStep) }}</small>
              <ol>
                <li v-for="step in command.steps" :key="step">{{ rpaStepLabel(step) }}</li>
              </ol>
              <div v-if="command.logs.length" class="rpa-task-logs">
                <code v-for="line in command.logs" :key="line">{{ line }}</code>
              </div>
              <a v-if="command.artifactUrl" class="artifact-link" :href="command.artifactUrl" target="_blank">
                {{ rpaCopy.artifact }}
              </a>
            </article>
          </div>
        </article>
      </section>

      <section class="content-grid">
        <article class="panel accounts-panel" id="accounts">
          <div class="panel-head">
            <div>
              <p class="eyebrow">{{ t.accountSupervision }}</p>
              <h2>{{ t.accounts }}</h2>
            </div>
            <div>
              <div class="segmented" role="group" :aria-label="t.accountFilter">
                <button
                  v-for="filter in accountFilters"
                  :key="filter"
                  :class="{ selected: selectedFilter === filter }"
                  @click="loadAccountsByStatus(filter)"
                >
                  {{ accountStatusLabel(filter) }}
                </button>
              </div>
              <small class="api-note">{{ t.accountsApiNote }}</small>
            </div>
          </div>

          <div class="account-list">
            <button
              v-for="account in accounts"
              :key="account.id"
              class="account-row"
              :class="{ selected: selectedAccountId === account.id }"
              @click="selectedAccountId = account.id"
            >
              <span>
                <strong>{{ account.name }}</strong>
                <small>{{ account.id }} · {{ account.desk }}</small>
              </span>
              <span class="status" :class="account.status.toLowerCase()">
                {{ accountStatusLabel(account.status) }}
              </span>
              <span class="number">{{ money(account.equity) }}</span>
              <span :class="['risk', account.riskLevel.toLowerCase()]">
                {{ riskLevelLabel(account.riskLevel) }}
              </span>
            </button>
          </div>
        </article>

        <article class="panel account-detail">
          <div class="panel-head">
            <div>
              <p class="eyebrow">{{ t.selectedAccount }}</p>
              <h2>{{ selectedAccount.name }}</h2>
            </div>
            <span class="status" :class="selectedAccount.status.toLowerCase()">
              {{ accountStatusLabel(selectedAccount.status) }}
            </span>
          </div>

          <div class="detail-grid">
            <div>
              <span>{{ t.equity }}</span>
              <strong>{{ money(selectedAccount.equity) }}</strong>
            </div>
            <div>
              <span>{{ t.cash }}</span>
              <strong>{{ money(selectedAccount.cash) }}</strong>
            </div>
            <div>
              <span>{{ t.exposure }}</span>
              <strong>{{ selectedAccount.exposure }}%</strong>
            </div>
            <div>
              <span>{{ t.dailyPnl }}</span>
              <strong :class="pnlClass(selectedAccount.dailyPnl)">
                {{ signedMoney(selectedAccount.dailyPnl) }}
              </strong>
            </div>
          </div>

          <div class="exposure-bar" :aria-label="t.exposure">
            <span :style="{ width: `${selectedAccount.exposure}%` }"></span>
          </div>
        </article>
      </section>

      <section class="content-grid wide-left">
        <article class="panel positions-panel">
          <div class="panel-head">
            <div>
              <p class="eyebrow">{{ t.portfolioView }}</p>
              <h2>{{ t.positions }}</h2>
            </div>
            <button class="icon-button" :title="t.refreshDashboard" @click="loadDashboard">↻</button>
          </div>

          <div class="table-wrap">
            <table>
              <thead>
                <tr>
                  <th>{{ t.instrument }}</th>
                  <th>{{ t.market }}</th>
                  <th>{{ t.qty }}</th>
                  <th>{{ t.last }}</th>
                  <th>{{ t.exposure }}</th>
                  <th>{{ t.dayPnl }}</th>
                  <th>{{ t.strategy }}</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="position in positions" :key="position.symbol">
                  <td>
                    <strong>{{ position.symbol }}</strong>
                    <small>{{ position.name }}</small>
                  </td>
                  <td>{{ position.market }}</td>
                  <td>{{ integer(position.quantity) }}</td>
                  <td>{{ price(position.last) }}</td>
                  <td>{{ money(position.exposure) }}</td>
                  <td :class="pnlClass(position.dayPnl)">{{ signedMoney(position.dayPnl) }}</td>
                  <td>{{ position.strategy }}</td>
                </tr>
              </tbody>
            </table>
          </div>
        </article>

        <article class="panel strategy-panel">
          <div class="panel-head">
            <div>
              <p class="eyebrow">{{ t.automationControls }}</p>
              <h2>{{ t.strategies }}</h2>
            </div>
          </div>

          <div class="strategy-list">
            <label v-for="strategy in strategyState" :key="strategy.id" class="strategy-card">
              <span>
                <strong>{{ strategyName(strategy) }}</strong>
                <small>{{ strategyGuardrail(strategy) }}</small>
              </span>
              <input v-model="strategy.enabled" type="checkbox" @change="saveStrategy(strategy)" />
            </label>
          </div>
        </article>
      </section>

      <section class="content-grid">
        <article class="panel" id="risk">
          <div class="panel-head">
            <div>
              <p class="eyebrow">{{ t.controls }}</p>
              <h2>{{ t.riskQueue }}</h2>
            </div>
            <div class="panel-actions">
              <span class="count-badge">{{ riskEvents.length }}</span>
              <div class="segmented compact" role="group" :aria-label="t.riskFilter">
                <button
                  v-for="level in riskFilters"
                  :key="level"
                  :class="{ selected: selectedRiskLevel === level }"
                  @click="loadRiskEventsByLevel(level)"
                >
                  {{ riskLevelLabel(level) }}
                </button>
              </div>
            </div>
          </div>
          <small class="api-note">{{ t.riskApiNote }}</small>

          <div class="risk-list">
            <article v-for="event in riskEvents" :key="event.id" class="risk-item">
              <span :class="['risk-dot', event.level.toLowerCase()]"></span>
              <div>
                <strong>{{ riskTitle(event) }}</strong>
                <p>{{ riskDetail(event) }}</p>
                <small>{{ event.createdAt }} · {{ riskOwner(event) }} · {{ event.id }}</small>
              </div>
            </article>
          </div>
        </article>

        <article class="panel" id="execution">
          <div class="panel-head">
            <div>
              <p class="eyebrow">{{ t.orderLifecycle }}</p>
              <h2>{{ t.executionTape }}</h2>
            </div>
          </div>

          <div class="timeline">
            <article v-for="event in executions" :key="`${event.time}-${event.symbol}`">
              <time>{{ event.time }}</time>
              <div>
                <strong>
                  {{ orderSideLabel(event.side) }} {{ integer(event.quantity) }} {{ event.symbol }}
                </strong>
                <span>{{ event.account }} · {{ event.note }}</span>
              </div>
              <span :class="['order-state', event.state.toLowerCase()]">
                {{ orderStateLabel(event.state) }}
              </span>
            </article>
          </div>
        </article>
      </section>
    </section>
  </main>
</template>

<script setup lang="ts">
import { computed, onMounted, onUnmounted, ref } from "vue";
import {
  fetchAccounts,
  fetchDashboard,
  fetchRiskEvents,
  fetchRpaCommands,
  submitRpaCommand,
  toggleStrategy
} from "./api";
import {
  accounts as demoAccounts,
  executions as demoExecutions,
  fallbackDashboard,
  positions as demoPositions,
  riskEvents as demoRiskEvents,
  strategyControls as demoStrategies,
  type Account,
  type AccountStatus,
  type OrderSide,
  type OrderState,
  type RiskEvent,
  type RiskLevel,
  type RpaAction,
  type RpaCommand,
  type RpaStatus,
  type StrategyControl
} from "./data";

type Locale = "en" | "zh" | "zhHant";
type AccountFilter = "All" | AccountStatus;
type RiskFilter = "All" | RiskLevel;

const dictionaries = {
  en: {
    brandTitle: "Trading Desk",
    brandSubtitle: "Operations Console",
    navOverview: "Overview",
    navAccounts: "Accounts",
    navRisk: "Risk Queue",
    navExecution: "Execution",
    portfolioProject: "Portfolio project",
    title: "Trading Operations Dashboard",
    heroCopy:
      "A production-inspired control surface for supervising multi-account equity trading, risk checks, automated strategy states, and execution follow-up.",
    singaporeSession: "Singapore session",
    metrics: "Portfolio metrics",
    totalEquity: "Total Equity",
    availableCash: "Available Cash",
    dailyPnl: "Daily P&L",
    activeOrders: "Active Orders",
    accountSupervision: "Account supervision",
    accounts: "Accounts",
    accountFilter: "Account filter",
    accountsApiNote: "Filter buttons call GET /api/accounts.",
    selectedAccount: "Selected account",
    equity: "Equity",
    cash: "Cash",
    exposure: "Exposure",
    portfolioView: "Portfolio view",
    positions: "Positions",
    refreshDashboard: "Refresh dashboard",
    instrument: "Instrument",
    market: "Market",
    qty: "Qty",
    last: "Last",
    dayPnl: "Day P&L",
    strategy: "Strategy",
    automationControls: "Automation controls",
    strategies: "Strategies",
    controls: "Controls",
    riskQueue: "Risk Queue",
    riskFilter: "Risk filter",
    riskApiNote: "Risk filter calls GET /api/risk-events.",
    orderLifecycle: "Order lifecycle",
    executionTape: "Execution Tape",
    language: "Language",
    demoData: "demo data",
    pythonPending: "Python API pending",
    livePythonApi: "Live Python API",
    offlineFallback: "Offline fallback data",
    strategySavedLocally: "Strategy saved locally",
    apiSnapshot: (time: string) => `API snapshot ${time}`,
    acrossAccounts: (count: number) => `Across ${count} supervised accounts`,
    cashRatio: (ratio: number) => `${ratio}% of portfolio equity`,
    pnlHint: "Realized and marked positions",
    riskItems: (count: number) => `${count} risk items need attention`
  },
  zh: {
    brandTitle: "交易台",
    brandSubtitle: "运营控制台",
    navOverview: "总览",
    navAccounts: "账户",
    navRisk: "风险队列",
    navExecution: "执行流水",
    portfolioProject: "作品集项目",
    title: "交易运营仪表盘",
    heroCopy: "用于监管多账户股票交易、风险检查、自动策略状态和执行跟进的全栈控制台。",
    singaporeSession: "新加坡交易时段",
    metrics: "组合指标",
    totalEquity: "总权益",
    availableCash: "可用现金",
    dailyPnl: "当日盈亏",
    activeOrders: "活跃订单",
    accountSupervision: "账户监管",
    accounts: "账户",
    accountFilter: "账户筛选",
    accountsApiNote: "筛选按钮会调用 GET /api/accounts。",
    selectedAccount: "当前账户",
    equity: "权益",
    cash: "现金",
    exposure: "敞口",
    portfolioView: "组合视图",
    positions: "持仓",
    refreshDashboard: "刷新仪表盘",
    instrument: "标的",
    market: "市场",
    qty: "数量",
    last: "最新价",
    dayPnl: "当日盈亏",
    strategy: "策略",
    automationControls: "自动化控制",
    strategies: "策略",
    controls: "控制项",
    riskQueue: "风险队列",
    riskFilter: "风险筛选",
    riskApiNote: "风险筛选会调用 GET /api/risk-events。",
    orderLifecycle: "订单生命周期",
    executionTape: "执行流水",
    language: "语言",
    demoData: "演示数据",
    pythonPending: "等待 Python API",
    livePythonApi: "已连接 Python API",
    offlineFallback: "离线备用数据",
    strategySavedLocally: "策略已本地保存",
    apiSnapshot: (time: string) => `API 快照 ${time}`,
    acrossAccounts: (count: number) => `覆盖 ${count} 个受监管账户`,
    cashRatio: (ratio: number) => `占组合权益 ${ratio}%`,
    pnlHint: "已实现和盯市持仓",
    riskItems: (count: number) => `${count} 个风险项需要关注`
  },
  zhHant: {
    brandTitle: "交易台",
    brandSubtitle: "營運控制台",
    navOverview: "總覽",
    navAccounts: "帳戶",
    navRisk: "風險佇列",
    navExecution: "執行流水",
    portfolioProject: "作品集專案",
    title: "交易營運儀表板",
    heroCopy: "用於監管多帳戶股票交易、風險檢查、自動策略狀態和執行跟進的全端控制台。",
    singaporeSession: "新加坡交易時段",
    metrics: "組合指標",
    totalEquity: "總權益",
    availableCash: "可用現金",
    dailyPnl: "當日損益",
    activeOrders: "活躍訂單",
    accountSupervision: "帳戶監管",
    accounts: "帳戶",
    accountFilter: "帳戶篩選",
    accountsApiNote: "篩選按鈕會呼叫 GET /api/accounts。",
    selectedAccount: "目前帳戶",
    equity: "權益",
    cash: "現金",
    exposure: "曝險",
    portfolioView: "組合視圖",
    positions: "持倉",
    refreshDashboard: "重新整理儀表板",
    instrument: "標的",
    market: "市場",
    qty: "數量",
    last: "最新價",
    dayPnl: "當日損益",
    strategy: "策略",
    automationControls: "自動化控制",
    strategies: "策略",
    controls: "控制項",
    riskQueue: "風險佇列",
    riskFilter: "風險篩選",
    riskApiNote: "風險篩選會呼叫 GET /api/risk-events。",
    orderLifecycle: "訂單生命週期",
    executionTape: "執行流水",
    language: "語言",
    demoData: "展示資料",
    pythonPending: "等待 Python API",
    livePythonApi: "已連接 Python API",
    offlineFallback: "離線備用資料",
    strategySavedLocally: "策略已本機儲存",
    apiSnapshot: (time: string) => `API 快照 ${time}`,
    acrossAccounts: (count: number) => `涵蓋 ${count} 個受監管帳戶`,
    cashRatio: (ratio: number) => `占組合權益 ${ratio}%`,
    pnlHint: "已實現和盯市持倉",
    riskItems: (count: number) => `${count} 個風險項需要關注`
  }
};

const accountStatusText = {
  en: { All: "All", Live: "Live", Review: "Review", Paused: "Paused" },
  zh: { All: "全部", Live: "运行中", Review: "复核", Paused: "暂停" },
  zhHant: { All: "全部", Live: "運行中", Review: "覆核", Paused: "暫停" }
};

const riskLevelText = {
  en: { All: "All", Low: "Low", Medium: "Medium", High: "High" },
  zh: { All: "全部", Low: "低", Medium: "中", High: "高" },
  zhHant: { All: "全部", Low: "低", Medium: "中", High: "高" }
};

const orderSideText = {
  en: { Buy: "Buy", Sell: "Sell" },
  zh: { Buy: "买入", Sell: "卖出" },
  zhHant: { Buy: "買入", Sell: "賣出" }
};

const orderStateText = {
  en: { Filled: "Filled", Working: "Working", Rejected: "Rejected" },
  zh: { Filled: "已成交", Working: "执行中", Rejected: "已拒绝" },
  zhHant: { Filled: "已成交", Working: "執行中", Rejected: "已拒絕" }
};

const strategyText: Record<
  Locale,
  Record<string, { name: string; guardrail: string }>
> = {
  en: {
    momentum: {
      name: "Momentum Guard",
      guardrail: "Max 18% single-name exposure"
    },
    reversion: {
      name: "Mean Reversion",
      guardrail: "Requires spread below 12 bps"
    },
    "manual-review": {
      name: "Manual Review",
      guardrail: "Trader approval for exceptions"
    }
  },
  zh: {
    momentum: {
      name: "动量防护",
      guardrail: "单一标的最大敞口 18%"
    },
    reversion: {
      name: "均值回归",
      guardrail: "要求价差低于 12 个基点"
    },
    "manual-review": {
      name: "人工复核",
      guardrail: "异常情况需要交易员审批"
    }
  },
  zhHant: {
    momentum: {
      name: "動量防護",
      guardrail: "單一標的最大曝險 18%"
    },
    reversion: {
      name: "均值回歸",
      guardrail: "要求價差低於 12 個基點"
    },
    "manual-review": {
      name: "人工覆核",
      guardrail: "異常情況需要交易員審批"
    }
  }
};

const riskEventText: Record<
  Locale,
  Record<string, { title: string; detail: string; owner: string }>
> = {
  en: {
    "R-1042": {
      title: "Exposure threshold approaching",
      detail: "Beta Income is within 6% of the configured exposure cap.",
      owner: "Ops Lead"
    },
    "R-1039": {
      title: "Stale quote recovered",
      detail: "HKEX market data feed recovered after one delayed tick.",
      owner: "System"
    },
    "R-1031": {
      title: "Manual approval required",
      detail: "One sell order exceeded the standard participation guardrail.",
      owner: "Trader"
    }
  },
  zh: {
    "R-1042": {
      title: "敞口接近阈值",
      detail: "Beta Income 距离已配置的敞口上限不足 6%。",
      owner: "运营负责人"
    },
    "R-1039": {
      title: "延迟报价已恢复",
      detail: "HKEX 行情源在一次延迟 tick 后恢复正常。",
      owner: "系统"
    },
    "R-1031": {
      title: "需要人工审批",
      detail: "一笔卖出订单超过了标准参与度风控限制。",
      owner: "交易员"
    }
  },
  zhHant: {
    "R-1042": {
      title: "曝險接近閾值",
      detail: "Beta Income 距離已配置的曝險上限不足 6%。",
      owner: "營運負責人"
    },
    "R-1039": {
      title: "延遲報價已恢復",
      detail: "HKEX 行情源在一次延遲 tick 後恢復正常。",
      owner: "系統"
    },
    "R-1031": {
      title: "需要人工審批",
      detail: "一筆賣出訂單超過了標準參與度風控限制。",
      owner: "交易員"
    }
  }
};

const rpaPanelText = {
  en: {
    eyebrow: "Backend automation",
    title: "RPA Operations",
    account: "Account",
    action: "Action",
    run: "Run RPA Command",
    running: "Submitting...",
    note: "This panel calls POST /api/rpa/commands and shows the backend command audit trail.",
    auditEyebrow: "Command audit",
    auditTitle: "RPA Command Log",
    artifact: "Open artifact"
  },
  zh: {
    eyebrow: "后端自动化",
    title: "RPA 操作",
    account: "账户",
    action: "动作",
    run: "执行 RPA 命令",
    running: "提交中...",
    note: "此面板会调用 POST /api/rpa/commands，并展示后端命令审计记录。",
    auditEyebrow: "命令审计",
    auditTitle: "RPA 命令日志",
    artifact: "打开产物"
  },
  zhHant: {
    eyebrow: "後端自動化",
    title: "RPA 操作",
    account: "帳戶",
    action: "動作",
    run: "執行 RPA 命令",
    running: "提交中...",
    note: "此面板會呼叫 POST /api/rpa/commands，並展示後端命令稽核記錄。",
    auditEyebrow: "命令稽核",
    auditTitle: "RPA 命令日誌",
    artifact: "開啟產物"
  }
};

const rpaActionText: Record<Locale, Record<RpaAction, string>> = {
  en: {
    refresh_positions: "Refresh positions",
    sync_orders: "Sync orders",
    export_statement: "Export statement"
  },
  zh: {
    refresh_positions: "刷新持仓",
    sync_orders: "同步委托",
    export_statement: "导出对账单"
  },
  zhHant: {
    refresh_positions: "刷新持倉",
    sync_orders: "同步委託",
    export_statement: "匯出對帳單"
  }
};

const rpaStatusText: Record<Locale, Record<RpaStatus, string>> = {
  en: { Queued: "Queued", Running: "Running", Completed: "Completed", Blocked: "Blocked", Failed: "Failed" },
  zh: { Queued: "已排队", Running: "执行中", Completed: "已完成", Blocked: "已拦截", Failed: "失败" },
  zhHant: { Queued: "已排隊", Running: "執行中", Completed: "已完成", Blocked: "已攔截", Failed: "失敗" }
};

const rpaMessageText: Record<Locale, Record<string, string>> = {
  en: {
    queuedRefresh: "Position refresh queued through the broker desktop workflow.",
    completedRefresh: "Position refresh completed through the broker desktop workflow.",
    queuedOrders: "Order synchronization queued through the broker entrustment workflow.",
    queuedStatement: "Statement export queued for back-office reconciliation.",
    blockedPaused: "Command blocked because the account is paused."
  },
  zh: {
    queuedRefresh: "已通过券商桌面流程排队刷新持仓。",
    completedRefresh: "已通过券商桌面流程完成持仓刷新。",
    queuedOrders: "已通过券商委托流程排队同步订单。",
    queuedStatement: "已排队导出对账单，用于后台核对。",
    blockedPaused: "账户已暂停，命令已被拦截。"
  },
  zhHant: {
    queuedRefresh: "已透過券商桌面流程排隊刷新持倉。",
    completedRefresh: "已透過券商桌面流程完成持倉刷新。",
    queuedOrders: "已透過券商委託流程排隊同步訂單。",
    queuedStatement: "已排隊匯出對帳單，用於後台核對。",
    blockedPaused: "帳戶已暫停，命令已被攔截。"
  }
};

const rpaStepText: Record<Locale, Record<string, string>> = {
  en: {},
  zh: {
    "Focus broker window": "聚焦券商窗口",
    "Open holdings tab": "打开持仓页签",
    "Trigger refresh": "触发刷新",
    "Read updated table": "读取更新后的表格",
    "Open order list": "打开委托列表",
    "Export working orders": "导出执行中订单",
    "Normalize order states": "标准化订单状态",
    "Open statement center": "打开对账单中心",
    "Select current trade date": "选择当前交易日",
    "Export file": "导出文件",
    "Register audit record": "登记审计记录",
    "Validate account status": "校验账户状态",
    "Stop before desktop automation": "在桌面自动化前停止"
  },
  zhHant: {
    "Focus broker window": "聚焦券商視窗",
    "Open holdings tab": "開啟持倉頁籤",
    "Trigger refresh": "觸發刷新",
    "Read updated table": "讀取更新後的表格",
    "Open order list": "開啟委託列表",
    "Export working orders": "匯出執行中訂單",
    "Normalize order states": "標準化訂單狀態",
    "Open statement center": "開啟對帳單中心",
    "Select current trade date": "選擇目前交易日",
    "Export file": "匯出檔案",
    "Register audit record": "登記稽核記錄",
    "Validate account status": "校驗帳戶狀態",
    "Stop before desktop automation": "在桌面自動化前停止"
  }
};

const dataSourceKeys = {
  pending: "pythonPending",
  live: "livePythonApi",
  fallback: "offlineFallback",
  local: "strategySavedLocally"
} as const;

const accountFilters: AccountFilter[] = ["All", "Live", "Review", "Paused"];
const riskFilters: RiskFilter[] = ["All", "Low", "Medium", "High"];

const locale = ref<Locale>("en");
const selectedFilter = ref<AccountFilter>("All");
const selectedRiskLevel = ref<RiskFilter>("All");
const accounts = ref<Account[]>([...demoAccounts]);
const positions = ref([...demoPositions]);
const riskEvents = ref([...demoRiskEvents]);
const executions = ref([...demoExecutions]);
const selectedAccountId = ref(accounts.value[0].id);
const refreshTick = ref(0);
const clock = ref("");
const dataSource = ref<keyof typeof dataSourceKeys>("pending");
const asOf = ref<string | undefined>(fallbackDashboard.asOf);
const strategyState = ref(demoStrategies.map((item) => ({ ...item })));
const allAccounts = ref<Account[]>([...demoAccounts]);
const rpaActions: RpaAction[] = ["refresh_positions", "sync_orders", "export_statement"];
const selectedRpaAccountId = ref(demoAccounts[0].id);
const selectedRpaAction = ref<RpaAction>("refresh_positions");
const rpaCommands = ref<RpaCommand[]>([...(fallbackDashboard.rpaCommands || [])]);
const rpaBusy = ref(false);
const rpaMessage = ref("");

const t = computed(() => dictionaries[locale.value]);
const rpaCopy = computed(() => rpaPanelText[locale.value]);
const dataSourceLabel = computed(() => t.value[dataSourceKeys[dataSource.value]]);
const totalEquity = computed(() => accounts.value.reduce((sum, item) => sum + item.equity, 0));
const totalCash = computed(() => accounts.value.reduce((sum, item) => sum + item.cash, 0));
const totalPnl = computed(() => accounts.value.reduce((sum, item) => sum + item.dailyPnl, 0));
const activeOrders = computed(() => accounts.value.reduce((sum, item) => sum + item.activeOrders, 0));
const highRiskCount = computed(() => riskEvents.value.filter((item) => item.level !== "Low").length);
const cashRatio = computed(() => Math.round((totalCash.value / totalEquity.value) * 100));
const asOfLabel = computed(() => {
  if (!asOf.value) return t.value.demoData;
  const timeLocale = locale.value === "en" ? "en-SG" : locale.value === "zh" ? "zh-CN" : "zh-TW";
  const time = new Date(asOf.value).toLocaleTimeString(timeLocale, {
    hour12: false
  });
  return t.value.apiSnapshot(time);
});

const selectedAccount = computed(() => {
  return accounts.value.find((item) => item.id === selectedAccountId.value) || demoAccounts[0];
});

let timer: number | undefined;
let rpaPollTimer: number | undefined;

function updateClock() {
  const clockLocale = locale.value === "en" ? "en-SG" : locale.value === "zh" ? "zh-CN" : "zh-TW";
  clock.value = new Intl.DateTimeFormat(clockLocale, {
    hour: "2-digit",
    minute: "2-digit",
    second: "2-digit",
    hour12: false,
    timeZone: "Asia/Singapore"
  }).format(new Date());
}

onMounted(() => {
  updateClock();
  loadDashboard();
  timer = window.setInterval(updateClock, 1000);
});

onUnmounted(() => {
  if (timer) window.clearInterval(timer);
  if (rpaPollTimer) window.clearInterval(rpaPollTimer);
});

function money(value: number) {
  return new Intl.NumberFormat("en-SG", {
    style: "currency",
    currency: "SGD",
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
  return new Intl.NumberFormat("en-SG", { maximumFractionDigits: 0 }).format(value);
}

function price(value: number) {
  return new Intl.NumberFormat("en-SG", {
    minimumFractionDigits: 2,
    maximumFractionDigits: 2
  }).format(value + refreshTick.value * 0);
}

function pnlClass(value: number) {
  if (value > 0) return "positive";
  if (value < 0) return "negative";
  return "";
}

function accountStatusLabel(status: AccountFilter) {
  return accountStatusText[locale.value][status];
}

function riskLevelLabel(level: RiskFilter) {
  return riskLevelText[locale.value][level];
}

function orderSideLabel(side: OrderSide) {
  return orderSideText[locale.value][side];
}

function orderStateLabel(state: OrderState) {
  return orderStateText[locale.value][state];
}

function strategyName(strategy: StrategyControl) {
  return strategyText[locale.value][strategy.id]?.name || strategy.name;
}

function strategyGuardrail(strategy: StrategyControl) {
  return strategyText[locale.value][strategy.id]?.guardrail || strategy.guardrail;
}

function riskTitle(event: RiskEvent) {
  return riskEventText[locale.value][event.id]?.title || event.title;
}

function riskDetail(event: RiskEvent) {
  return riskEventText[locale.value][event.id]?.detail || event.detail;
}

function riskOwner(event: RiskEvent) {
  return riskEventText[locale.value][event.id]?.owner || event.owner;
}

function rpaActionLabel(action: RpaAction) {
  return rpaActionText[locale.value][action];
}

function rpaStatusLabel(status: RpaStatus) {
  return rpaStatusText[locale.value][status];
}

function rpaMessageLabel(command: RpaCommand) {
  if (command.status === "Blocked") return rpaMessageText[locale.value].blockedPaused;
  if (command.action === "refresh_positions" && command.status === "Completed") {
    return rpaMessageText[locale.value].completedRefresh;
  }
  if (command.action === "refresh_positions") return rpaMessageText[locale.value].queuedRefresh;
  if (command.action === "sync_orders") return rpaMessageText[locale.value].queuedOrders;
  return rpaMessageText[locale.value].queuedStatement;
}

function rpaStepLabel(step: string) {
  return rpaStepText[locale.value][step] || step;
}

function hasActiveRpaCommands(commands = rpaCommands.value) {
  return commands.some((item) => item.status === "Queued" || item.status === "Running");
}

function syncSelectedAccount() {
  if (!accounts.value.some((item) => item.id === selectedAccountId.value)) {
    selectedAccountId.value = accounts.value[0]?.id || demoAccounts[0].id;
  }
  if (!allAccounts.value.some((item) => item.id === selectedRpaAccountId.value)) {
    selectedRpaAccountId.value = allAccounts.value[0]?.id || demoAccounts[0].id;
  }
}

async function loadDashboard() {
  refreshTick.value += 1;
  try {
    const dashboard = await fetchDashboard();
    accounts.value = dashboard.accounts;
    allAccounts.value = dashboard.accounts;
    positions.value = dashboard.positions;
    riskEvents.value = dashboard.riskEvents;
    executions.value = dashboard.executions;
    strategyState.value = dashboard.strategies.map((item) => ({ ...item }));
    rpaCommands.value = dashboard.rpaCommands || [];
    asOf.value = dashboard.asOf;
    selectedFilter.value = "All";
    selectedRiskLevel.value = "All";
    dataSource.value = "live";
    syncSelectedAccount();
  } catch {
    accounts.value = fallbackDashboard.accounts;
    allAccounts.value = fallbackDashboard.accounts;
    positions.value = fallbackDashboard.positions;
    riskEvents.value = fallbackDashboard.riskEvents;
    executions.value = fallbackDashboard.executions;
    strategyState.value = fallbackDashboard.strategies.map((item) => ({ ...item }));
    rpaCommands.value = fallbackDashboard.rpaCommands || [];
    asOf.value = undefined;
    dataSource.value = "fallback";
    syncSelectedAccount();
  }
}

async function loadAccountsByStatus(status: AccountFilter) {
  selectedFilter.value = status;
  try {
    accounts.value = await fetchAccounts(status);
    dataSource.value = "live";
  } catch {
    accounts.value =
      status === "All"
        ? fallbackDashboard.accounts
        : fallbackDashboard.accounts.filter((item) => item.status === status);
    dataSource.value = "fallback";
  }
  syncSelectedAccount();
}

async function loadRiskEventsByLevel(level: RiskFilter) {
  selectedRiskLevel.value = level;
  try {
    riskEvents.value = await fetchRiskEvents(level);
    dataSource.value = "live";
  } catch {
    riskEvents.value =
      level === "All"
        ? fallbackDashboard.riskEvents
        : fallbackDashboard.riskEvents.filter((item) => item.level === level);
    dataSource.value = "fallback";
  }
}

async function saveStrategy(strategy: (typeof strategyState.value)[number]) {
  try {
    const updated = await toggleStrategy(strategy);
    strategy.enabled = updated.enabled;
    dataSource.value = "live";
  } catch {
    dataSource.value = "local";
  }
}

async function runRpaCommand() {
  rpaBusy.value = true;
  rpaMessage.value = "";
  try {
    const command = await submitRpaCommand(selectedRpaAccountId.value, selectedRpaAction.value);
    rpaCommands.value = [command, ...rpaCommands.value.filter((item) => item.id !== command.id)];
    dataSource.value = "live";
    rpaMessage.value = `${command.id}: ${rpaMessageLabel(command)}`;
    rpaCommands.value = await fetchRpaCommands();
    startRpaPolling();
  } catch {
    const fallbackCommand: RpaCommand = {
      id: `RPA-DEMO-${Date.now().toString().slice(-4)}`,
      accountId: selectedRpaAccountId.value,
      action: selectedRpaAction.value,
      status: "Queued",
      createdAt: new Date().toLocaleTimeString("en-SG", { hour12: false }),
      operator: "Dashboard Demo",
      message: "Offline demo command queued locally.",
      steps: ["Focus broker window", "Open holdings tab", "Trigger refresh", "Read updated table"],
      progress: 0,
      currentStep: "Waiting for scheduler",
      artifactUrl: "",
      logs: ["Offline fallback command created in browser"]
    };
    rpaCommands.value = [fallbackCommand, ...rpaCommands.value];
    dataSource.value = "local";
    rpaMessage.value = `${fallbackCommand.id}: ${rpaMessageLabel(fallbackCommand)}`;
  } finally {
    rpaBusy.value = false;
  }
}

function startRpaPolling() {
  if (rpaPollTimer) window.clearInterval(rpaPollTimer);
  rpaPollTimer = window.setInterval(async () => {
    try {
      const commands = await fetchRpaCommands();
      rpaCommands.value = commands;
      if (!hasActiveRpaCommands(commands) && rpaPollTimer) {
        window.clearInterval(rpaPollTimer);
        rpaPollTimer = undefined;
      }
    } catch {
      if (rpaPollTimer) {
        window.clearInterval(rpaPollTimer);
        rpaPollTimer = undefined;
      }
    }
  }, 700);
}
</script>
