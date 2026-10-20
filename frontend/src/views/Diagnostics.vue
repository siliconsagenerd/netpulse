<script setup lang="ts">
import { ref, onMounted } from "vue";
import { useI18n } from "../i18n";
import { api } from "../services/api";
import type { Run, Event, Rule, Client, Domain } from "../types";

const { t } = useI18n();
const form = ref({ seed: 42, duration_seconds: 10, request_rate: 8, cache_ttl: 30, cache_capacity: 50, cache_policy: "lru" });
const rules = ref<Rule[]>([]);
const clients = ref<Client[]>([]);
const domains = ref<Domain[]>([]);
const newRule = ref({ name: "", priority: 100, action: "allow", match_client: "*", match_domain: "*", rate_limit_per_min: null as number | null, route_to: null as string | null, reason: null as string | null });
const editingId = ref<string | null>(null);
const pendingDelete = ref<string | null>(null);
const loading = ref(false);
const rulesLoading = ref(false);
const err = ref("");
const success = ref("");
const running = ref(false);
const run = ref<Run | null>(null);
const events = ref<Event[]>([]);
const filterAction = ref("");
const filterClient = ref("");
const filterDomain = ref("");
const offset = ref(0);
const limit = ref(50);
const hasMore = ref(false);

async function loadRules() {
  rulesLoading.value = true;
  try { rules.value = await api.rules(); }
  catch (e: any) { err.value = e.message; }
  finally { rulesLoading.value = false; }
}
async function loadRefs() {
  try { clients.value = await api.clients(); domains.value = await api.domains(); } catch {}
}
async function addRule() {
  err.value = ""; success.value = "";
  if (!newRule.value.name.trim()) { err.value = "Name is required"; return; }
  if (newRule.value.action === "rate_limit" && !newRule.value.rate_limit_per_min) { err.value = "rate_limit_per_min is required"; return; }
  if (newRule.value.action === "route" && !newRule.value.route_to) { err.value = "route_to is required"; return; }
  try {
    if (editingId.value) {
      await api.updateRule(editingId.value, newRule.value);
      success.value = t("rules.updated");
    } else {
      await api.createRule(newRule.value);
      success.value = t("rules.added");
    }
    resetRuleForm();
    await loadRules();
  } catch (e: any) { err.value = e.message; }
}
function editRule(r: Rule) {
  editingId.value = r.id;
  newRule.value = {
    name: r.name, priority: r.priority, action: r.action,
    match_client: r.match_client, match_domain: r.match_domain,
    rate_limit_per_min: r.rate_limit_per_min ?? null,
    route_to: r.route_to ?? null, reason: r.reason ?? null,
  };
}
function resetRuleForm() {
  editingId.value = null;
  newRule.value = { name: "", priority: 100, action: "allow", match_client: "*", match_domain: "*", rate_limit_per_min: null, route_to: null, reason: null };
}
function askDelete(id: string) { pendingDelete.value = id; }
async function confirmDelete() {
  const id = pendingDelete.value; if (!id) return;
  pendingDelete.value = null;
  err.value = ""; success.value = "";
  try { await api.deleteRule(id); success.value = t("rules.deleted"); await loadRules(); }
  catch (e: any) { err.value = e.message; }
}
function cancelDelete() { pendingDelete.value = null; }
async function togRule(id: string) {
  err.value = ""; success.value = "";
  try { await api.toggleRule(id); await loadRules(); }
  catch (e: any) { err.value = e.message; }
}

async function start() {
  running.value = true; err.value = ""; success.value = "";
  try {
    run.value = await api.simulate(form.value);
    offset.value = 0;
    await reloadEvents();
  } catch (e: any) { err.value = e.message; }
  finally { running.value = false; }
}
async function reloadEvents() {
  if (!run.value) return;
  loading.value = true;
  try {
    const params: any = { limit: limit.value, offset: offset.value };
    if (filterAction.value) params.action = filterAction.value;
    if (filterClient.value) params.client = filterClient.value;
    if (filterDomain.value) params.domain = filterDomain.value;
    const data = await api.events(run.value.id, params);
    events.value = data;
    hasMore.value = data.length >= limit.value;
  } catch (e: any) { err.value = e.message; }
  finally { loading.value = false; }
}
function nextPage() { offset.value += limit.value; reloadEvents(); }
function prevPage() { offset.value = Math.max(0, offset.value - limit.value); reloadEvents(); }

onMounted(() => { loadRules(); loadRefs(); });
</script>

<template>
  <div>
    <h1>{{ t("diagnostics.title") }}</h1>
    <div v-if="err" class="empty" role="alert">{{ err }}</div>
    <div v-if="success" class="card" role="status" style="background:var(--surface-2); margin-bottom:12px">{{ success }}</div>

    <div class="card" style="margin-bottom:16px">
      <div class="grid grid-3">
        <div><label class="kpi-label">{{ t("diagnostics.seed") }}</label><input class="input" type="number" v-model.number="form.seed" /></div>
        <div><label class="kpi-label">{{ t("diagnostics.duration") }}</label><input class="input" type="number" v-model.number="form.duration_seconds" /></div>
        <div><label class="kpi-label">{{ t("diagnostics.rate") }}</label><input class="input" type="number" v-model.number="form.request_rate" /></div>
        <div><label class="kpi-label">{{ t("diagnostics.ttl") }}</label><input class="input" type="number" v-model.number="form.cache_ttl" /></div>
        <div><label class="kpi-label">{{ t("diagnostics.capacity") }}</label><input class="input" type="number" v-model.number="form.cache_capacity" /></div>
      </div>
      <div style="margin-top:12px">
        <button class="btn" :disabled="running" @click="start">{{ running ? t("diagnostics.running") : t("diagnostics.run") }}</button>
      </div>
    </div>

    <div v-if="run" class="card" style="margin-bottom:16px">
      <div class="grid grid-3" style="margin-bottom:12px">
        <div><div class="kpi-label">Events</div><div class="kpi">{{ run.summary?.total_events }}</div></div>
        <div><div class="kpi-label">Hit%</div><div class="kpi">{{ ((run.summary?.cache_hit_ratio ?? 0)*100).toFixed(1) }}%</div></div>
        <div><div class="kpi-label">Blocked</div><div class="kpi">{{ run.summary?.blocked }}</div></div>
      </div>
      <div style="display:flex; gap:8px; align-items:center; margin-bottom:8px; flex-wrap:wrap">
        <label class="kpi-label">{{ t("diagnostics.filterAction") }}</label>
        <select class="input" style="width:auto" v-model="filterAction" @change="() => { offset = 0; reloadEvents(); }">
          <option value="">{{ t("diagnostics.all") }}</option>
          <option value="allow">allow</option>
          <option value="block">block</option>
          <option value="rate_limit">rate_limit</option>
          <option value="route">route</option>
        </select>
        <label class="kpi-label">client</label>
        <select class="input" style="width:auto" v-model="filterClient" @change="() => { offset = 0; reloadEvents(); }">
          <option value="">all</option>
          <option v-for="c in clients" :key="c.id" :value="c.name">{{ c.name }}</option>
        </select>
        <label class="kpi-label">domain</label>
        <select class="input" style="width:auto" v-model="filterDomain" @change="() => { offset = 0; reloadEvents(); }">
          <option value="">all</option>
          <option v-for="d in domains" :key="d.id" :value="d.name">{{ d.name }}</option>
        </select>
      </div>
      <div v-if="loading" class="empty">{{ t("loading") }}</div>
      <div v-else-if="!events.length" class="empty">{{ t("empty") }}</div>
      <div v-else style="max-height:420px; overflow:auto; width:100%; max-width:100%">
        <table class="table" style="min-width:640px">
          <thead><tr><th>ts</th><th>client</th><th>domain</th><th>action</th><th>cache</th><th>ms</th><th>status</th></tr></thead>
          <tbody>
            <tr v-for="e in events" :key="e.id">
              <td class="mono">{{ e.ts.toFixed(2) }}</td>
              <td class="mono">{{ e.client }}</td>
              <td class="mono">{{ e.domain }}</td>
              <td><span class="badge" :class="'badge-'+e.action">{{ e.action }}</span></td>
              <td>{{ e.cache }}</td>
              <td>{{ e.latency_ms }}</td>
              <td>{{ e.status_code }}</td>
            </tr>
          </tbody>
        </table>
      </div>
      <div v-if="events.length" style="display:flex; gap:8px; margin-top:8px">
        <button class="btn btn-secondary" :disabled="offset===0" @click="prevPage">{{ t("prev") }}</button>
        <button class="btn btn-secondary" :disabled="!hasMore" @click="nextPage">{{ t("next") }}</button>
        <span class="kpi-label" style="align-self:center">offset {{ offset }}</span>
      </div>
    </div>

    <div class="card" style="margin-top:16px">
      <h3>{{ t("rules.title") }}</h3>
      <div class="grid grid-3" style="margin-bottom:8px">
        <input class="input" v-model="newRule.name" :placeholder="t('rules.name')" />
        <input class="input" type="number" v-model.number="newRule.priority" :placeholder="t('rules.priority')" />
        <select class="input" v-model="newRule.action">
          <option value="allow">allow</option>
          <option value="block">block</option>
          <option value="rate_limit">rate_limit</option>
          <option value="route">route</option>
        </select>
      </div>
      <div class="grid grid-2" style="margin-bottom:8px">
        <input class="input" v-model="newRule.match_client" :placeholder="t('rules.matchClient')" />
        <input class="input" v-model="newRule.match_domain" :placeholder="t('rules.matchDomain')" />
      </div>
      <div class="grid grid-2" style="margin-bottom:8px">
        <input class="input" type="number" v-model.number="newRule.rate_limit_per_min" placeholder="rate_limit_per_min (rate_limit)" />
        <input class="input" v-model="newRule.route_to" placeholder="route_to (route)" />
      </div>
      <div style="margin-bottom:8px">
        <input class="input" v-model="newRule.reason" :placeholder="t('rules.reason')" style="width:100%" />
      </div>
      <div style="display:flex; gap:8px">
        <button class="btn" @click="addRule">{{ editingId ? t("rules.save") : t("rules.add") }}</button>
        <button v-if="editingId" class="btn btn-secondary" @click="resetRuleForm">{{ t("rules.cancel") }}</button>
      </div>

      <div v-if="rulesLoading" class="empty">{{ t("loading") }}</div>
      <div v-else-if="!rules.length" class="empty">{{ t("empty") }}</div>
      <div v-if="pendingDelete" class="card" role="alertdialog" style="margin:12px 0; display:flex; gap:8px; align-items:center">
        <span>{{ t("rules.confirmDelete") }}</span>
        <button class="btn btn-danger" @click="confirmDelete">Yes</button>
        <button class="btn btn-secondary" @click="cancelDelete">No</button>
      </div>
      <div v-else style="overflow:auto; width:100%; max-width:100%; margin-top:12px">
        <table class="table" style="min-width:640px">
        <thead><tr><th>{{ t("rules.name") }}</th><th>{{ t("rules.priority") }}</th><th>{{ t("rules.action") }}</th><th>match</th><th>params</th><th>enabled</th><th></th></tr></thead>
        <tbody>
          <tr v-for="r in rules" :key="r.id">
            <td>{{ r.name }}</td>
            <td class="mono">{{ r.priority }}</td>
            <td><span class="badge" :class="'badge-'+r.action">{{ r.action }}</span></td>
            <td class="mono">{{ r.match_client }} / {{ r.match_domain }}</td>
            <td class="mono">{{ r.rate_limit_per_min ?? r.route_to ?? r.reason ?? "-" }}</td>
            <td>{{ r.enabled ? "✓" : "✗" }}</td>
            <td style="display:flex; gap:4px; flex-wrap:wrap">
              <button class="btn btn-secondary" @click="editRule(r)">{{ t("rules.edit") }}</button>
              <button class="btn btn-secondary" @click="togRule(r.id)">{{ t("rules.toggle") }}</button>
              <button class="btn btn-danger" @click="askDelete(r.id)">{{ t("rules.delete") }}</button>
            </td>
          </tr>
        </tbody>
      </table>
      </div>
    </div>
  </div>
</template>
