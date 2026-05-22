<template>
  <main class="app-shell">
    <aside class="sidebar" aria-label="Dashboard navigation">
      <div class="brand">
        <div class="brand-mark">TO</div>
        <div>
          <strong>Trading Operations</strong>
          <span>Sanitized portfolio demo</span>
        </div>
      </div>

      <nav>
        <a href="#accounts">Accounts</a>
        <a href="#holdings">Holdings</a>
        <a href="#strategy">Profiles</a>
        <a href="#logs">Logs</a>
      </nav>

      <div class="admin-card">
        <label for="admin-key">Demo admin key</label>
        <div class="admin-input">
          <input
            id="admin-key"
            :value="store.adminKey"
            type="password"
            placeholder="Stored locally"
            @input="store.saveAdminKey(($event.target as HTMLInputElement).value)"
          />
          <span :class="{ ready: store.hasAdminKey }">{{ store.hasAdminKey ? "Set" : "Empty" }}</span>
        </div>
      </div>
    </aside>

    <section class="workspace">
      <header class="topbar">
        <div>
          <p class="eyebrow">Vue 3 + TypeScript + Pinia</p>
          <h1>Trading Operations Dashboard</h1>
          <p>
            A frontend-focused full-stack demo for monitoring mock multi-account portfolio operations,
            status checks, profile settings, and sanitized activity logs.
          </p>
        </div>
        <div class="topbar-actions">
          <span class="snapshot">Snapshot {{ snapshotTime }}</span>
          <button class="secondary-button" @click="store.resetDemo">Reset cache</button>
          <button class="primary-button" @click="store.loadDashboard">Refresh</button>
        </div>
      </header>

      <section v-if="store.loadState === 'loading'" class="state-panel">Loading sanitized mock data...</section>
      <section v-else-if="store.loadState === 'error'" class="state-panel error">{{ store.error }}</section>

      <section class="kpi-grid" aria-label="Portfolio summary">
        <article class="metric">
          <span>Total equity</span>
          <strong>{{ money(store.totalEquity) }}</strong>
          <small>{{ store.accounts.length }} supervised demo accounts</small>
        </article>
        <article class="metric">
          <span>Available cash</span>
          <strong>{{ money(store.totalCash) }}</strong>
          <small>{{ cashRatio }}% of total equity</small>
        </article>
        <article class="metric">
          <span>Daily P&amp;L</span>
          <strong :class="pnlClass(store.totalPnl)">{{ signedMoney(store.totalPnl) }}</strong>
          <small>Mock marked positions only</small>
        </article>
        <article class="metric">
          <span>Open tickets</span>
          <strong>{{ store.openTickets }}</strong>
          <small>Operational review queue</small>
        </article>
      </section>

      <section class="server-grid" aria-label="Server status">
        <article v-for="server in store.servers" :key="server.id" class="server-card">
          <div>
            <span :class="['status-dot', server.status.toLowerCase()]"></span>
            <strong>{{ server.name }}</strong>
            <small>{{ server.region }}</small>
          </div>
          <dl>
            <div>
              <dt>Latency</dt>
              <dd>{{ server.latencyMs }} ms</dd>
            </div>
            <div>
              <dt>Queue</dt>
              <dd>{{ server.queueDepth }}</dd>
            </div>
            <div>
              <dt>Heartbeat</dt>
              <dd>{{ server.lastHeartbeat }}</dd>
            </div>
          </dl>
        </article>
      </section>

      <section class="content-grid" id="accounts">
        <article class="panel">
          <div class="panel-head">
            <div>
              <p class="eyebrow">Multi-account dashboard</p>
              <h2>Accounts</h2>
            </div>
            <div class="filter-row">
              <select v-model="store.accountStatus" aria-label="Account status">
                <option value="All">All statuses</option>
                <option value="Active">Active</option>
                <option value="Review">Review</option>
                <option value="Paused">Paused</option>
              </select>
              <select v-model="store.riskLevel" aria-label="Risk level">
                <option value="All">All risk levels</option>
                <option value="Low">Low</option>
                <option value="Medium">Medium</option>
                <option value="High">High</option>
              </select>
            </div>
          </div>

          <div v-if="store.filteredAccounts.length === 0" class="empty-state">
            No accounts match the current filters.
          </div>
          <div v-else class="account-list">
            <article v-for="account in store.filteredAccounts" :key="account.id" class="account-row">
              <div>
                <strong>{{ account.name }}</strong>
                <small>{{ account.id }} · {{ account.desk }}</small>
              </div>
              <span :class="['pill', account.status.toLowerCase()]">{{ account.status }}</span>
              <span class="number">{{ money(account.equity) }}</span>
              <span :class="['risk', account.riskLevel.toLowerCase()]">{{ account.riskLevel }}</span>
            </article>
          </div>
        </article>

        <article class="panel">
          <div class="panel-head">
            <div>
              <p class="eyebrow">Grouped by symbol</p>
              <h2>Exposure Rollup</h2>
            </div>
          </div>
          <div class="rollup-list">
            <article v-for="holding in store.groupedHoldings" :key="holding.symbol" class="rollup-row">
              <div>
                <strong>{{ holding.symbol }}</strong>
                <small>{{ holding.name }} · {{ holding.accounts }} accounts</small>
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
            <p class="eyebrow">Sorting, filtering, optimistic updates</p>
            <h2>Portfolio Holdings</h2>
          </div>
          <div class="filter-row wide">
            <input v-model="store.holdingQuery" type="search" placeholder="Filter symbol, name, or market" />
            <select v-model="store.selectedAccountId" aria-label="Holding account filter">
              <option value="All">All accounts</option>
              <option v-for="account in store.accounts" :key="account.id" :value="account.id">
                {{ account.name }}
              </option>
            </select>
            <select v-model="store.selectedProfile" aria-label="Profile filter">
              <option value="All">All profiles</option>
              <option value="A">Profile A</option>
              <option value="B">Profile B</option>
            </select>
          </div>
        </div>

        <p v-if="store.optimisticMessage" class="inline-notice">{{ store.optimisticMessage }}</p>

        <div class="table-wrap">
          <table>
            <thead>
              <tr>
                <th><button @click="store.setSort('symbol')">Symbol {{ sortMark("symbol") }}</button></th>
                <th>Account</th>
                <th><button @click="store.setSort('market')">Market {{ sortMark("market") }}</button></th>
                <th><button @click="store.setSort('quantity')">Qty {{ sortMark("quantity") }}</button></th>
                <th>Last</th>
                <th><button @click="store.setSort('exposure')">Exposure {{ sortMark("exposure") }}</button></th>
                <th><button @click="store.setSort('dayPnl')">Day P&amp;L {{ sortMark("dayPnl") }}</button></th>
                <th><button @click="store.setSort('profile')">Profile {{ sortMark("profile") }}</button></th>
              </tr>
            </thead>
            <tbody>
              <tr v-if="store.filteredHoldings.length === 0">
                <td colspan="8" class="empty-cell">No holdings match the filters.</td>
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
                    aria-label="Move holding to profile"
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
              <p class="eyebrow">Strategy configuration modal</p>
              <h2>A/B Profile Configuration</h2>
            </div>
          </div>
          <div class="profile-list">
            <article v-for="profile in store.strategies" :key="profile.id" class="profile-card">
              <div>
                <strong>{{ profile.label }}</strong>
                <small>Max single-name exposure: {{ profile.maxSingleNameExposure }}%</small>
                <small>Window: {{ profile.rebalanceWindow }}</small>
              </div>
              <button class="secondary-button" @click="openProfile(profile)">Configure</button>
            </article>
          </div>
        </article>

        <article class="panel" id="logs">
          <div class="panel-head">
            <div>
              <p class="eyebrow">Mock real-time stream</p>
              <h2>Operations Log</h2>
            </div>
            <button class="secondary-button" @click="addMockLog">Add log</button>
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
            <p class="eyebrow">Profile {{ editingProfile.variant }}</p>
            <h2>{{ editingProfile.label }}</h2>
          </div>
          <button class="icon-button" type="button" aria-label="Close modal" @click="editingProfile = null">×</button>
        </div>

        <label>
          <span>Max single-name exposure</span>
          <input v-model.number="editingProfile.maxSingleNameExposure" min="1" max="50" type="number" />
        </label>
        <label>
          <span>Review window</span>
          <input v-model="editingProfile.rebalanceWindow" type="text" />
        </label>
        <label class="checkbox-row">
          <input v-model="editingProfile.alertsEnabled" type="checkbox" />
          <span>Enable review alerts</span>
        </label>
        <label>
          <span>Demo notes</span>
          <textarea v-model="editingProfile.notes" rows="4"></textarea>
        </label>

        <div class="modal-actions">
          <button class="secondary-button" type="button" @click="editingProfile = null">Cancel</button>
          <button class="primary-button" type="submit">Save profile</button>
        </div>
      </form>
    </div>
  </main>
</template>

<script setup lang="ts">
import { computed, onMounted, onUnmounted, ref } from "vue";
import { useDashboardStore } from "../stores/dashboard";
import type { Holding, ProfileVariant, StrategyProfile } from "../data";

const store = useDashboardStore();
const editingProfile = ref<StrategyProfile | null>(null);
let logTimer: number | undefined;

const snapshotTime = computed(() => {
  return new Date(store.asOf).toLocaleTimeString("en-US", { hour12: false });
});

const cashRatio = computed(() => {
  if (!store.totalEquity) return 0;
  return Math.round((store.totalCash / store.totalEquity) * 100);
});

onMounted(() => {
  store.loadDashboard();
  logTimer = window.setInterval(() => {
    store.pushLog("info", "mock-feed", "Simulated heartbeat received from local mock service.");
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
  store.pushLog("warning", "review-queue", "Manual review item added to the sanitized demo log.");
}

function accountName(accountId: Holding["accountId"]) {
  return store.accounts.find((account) => account.id === accountId)?.name || accountId;
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
  return store.sortDirection === "asc" ? "↑" : "↓";
}
</script>
