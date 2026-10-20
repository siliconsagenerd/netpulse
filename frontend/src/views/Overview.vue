<script setup lang="ts">
import { ref, onMounted } from "vue";
import { useI18n } from "../i18n";
import { api } from "../services/api";
import type { Run, Dashboard } from "../types";

const { t } = useI18n();
const runs = ref<Run[]>([]);
const latest = ref<Run | null>(null);
const dash = ref<Dashboard | null>(null);
const loading = ref(true);
const err = ref("");

onMounted(async () => {
  try {
    runs.value = await api.runs();
    latest.value = runs.value[0] || null;
    if (latest.value) dash.value = await api.dashboard(latest.value.id);
  } catch (e: any) {
    err.value = e.message;
  } finally {
    loading.value = false;
  }
});
</script>

<template>
  <div>
    <h1>{{ t("overview.title") }}</h1>
    <p class="simulated-tag">{{ t("overview.subtitle") }} · {{ t("simulated") }}</p>

    <div v-if="loading" class="empty">{{ t("loading") }}</div>
    <div v-else-if="err" class="empty">{{ t("error") }}: {{ err }}</div>
    <div v-else-if="!latest" class="empty">
      {{ t("overview.noRuns") }}
      <div style="margin-top:12px"><RouterLink to="/diagnostics" class="btn">{{ t("nav.diagnostics") }}</RouterLink></div>
    </div>
    <template v-else>
      <div class="grid grid-3" style="margin-bottom:16px">
        <div class="card"><div class="kpi-label">{{ t("overview.totalEvents") }}</div><div class="kpi">{{ dash?.summary?.total_events ?? 0 }}</div></div>
        <div class="card"><div class="kpi-label">{{ t("overview.cacheHit") }}</div><div class="kpi">{{ ((dash?.summary?.cache_hit_ratio ?? 0)*100).toFixed(1) }}%</div></div>
        <div class="card"><div class="kpi-label">{{ t("overview.blocked") }}</div><div class="kpi">{{ dash?.summary?.blocked ?? 0 }}</div></div>
        <div class="card"><div class="kpi-label">{{ t("overview.avgLatency") }}</div><div class="kpi">{{ dash?.summary?.avg_latency_ms ?? 0 }}</div></div>
      </div>

      <div class="card" style="margin-bottom:16px">
        <h3>{{ t("overview.recentRuns") }}</h3>
        <table class="table">
          <thead><tr><th>Run</th><th>Seed</th><th>Events</th><th>Hit%</th><th>Started</th></tr></thead>
          <tbody>
            <tr v-for="r in runs.slice(0,8)" :key="r.id">
              <td class="mono">{{ r.id.slice(0,8) }}</td>
              <td class="mono">{{ r.seed }}</td>
              <td>{{ r.summary?.total_events ?? "-" }}</td>
              <td>{{ r.summary ? (r.summary.cache_hit_ratio*100).toFixed(1)+'%' : "-" }}</td>
              <td class="mono">{{ new Date(r.started_at).toLocaleString() }}</td>
            </tr>
          </tbody>
        </table>
      </div>
    </template>
  </div>
</template>
