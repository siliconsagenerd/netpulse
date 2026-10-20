<script setup lang="ts">
import { ref, onMounted } from "vue";
import { useI18n } from "../i18n";
import { api } from "../services/api";
import type { Run, Report } from "../types";

const { t } = useI18n();
const runs = ref<Run[]>([]);
const selected = ref("");
const report = ref<Report | null>(null);

async function load() {
  runs.value = await api.runs();
  if (runs.value.length && !selected.value) selected.value = runs.value[0].id;
  await fetchReport();
}
async function fetchReport() {
  if (!selected.value) return;
  report.value = await api.report(selected.value);
}
function download() {
  if (!report.value) return;
  const blob = new Blob([JSON.stringify(report.value, null, 2)], { type: "application/json" });
  const url = URL.createObjectURL(blob);
  const a = document.createElement("a");
  a.href = url; a.download = `netpulse-report-${report.value.run_id}.json`;
  a.click(); URL.revokeObjectURL(url);
}
onMounted(load);
</script>

<template>
  <div>
    <h1>{{ t("reports.title") }}</h1>
    <div class="card" style="margin-bottom:16px; display:flex; gap:8px; align-items:center; flex-wrap:wrap">
      <select class="input" style="width:auto" v-model="selected" @change="fetchReport">
        <option v-for="r in runs" :key="r.id" :value="r.id">{{ r.id.slice(0,8) }}</option>
      </select>
      <button class="btn" @click="download">{{ t("reports.download") }}</button>
    </div>
    <div v-if="report" class="grid">
      <div class="card">
        <h3>{{ t("reports.assertions") }}</h3>
        <ul>
          <li v-for="a in report.assertions" :key="a.name" :style="{ color: a.passed ? 'var(--success)' : 'var(--danger)' }">
            {{ a.passed ? "✓" : "✗" }} {{ a.name }}
          </li>
        </ul>
      </div>
      <div class="card">
        <h3>{{ t("reports.limitations") }}</h3>
        <ul><li v-for="l in report.limitations" :key="l">{{ l }}</li></ul>
      </div>
      <div class="card">
        <h3>{{ t("reports.sample") }} ({{ report.total_events }})</h3>
        <div style="max-height:300px; overflow:auto">
          <table class="table">
            <thead><tr><th>ts</th><th>client</th><th>domain</th><th>action</th><th>cache</th></tr></thead>
            <tbody>
              <tr v-for="e in report.events_sample" :key="e.id">
                <td class="mono">{{ e.ts.toFixed(2) }}</td>
                <td class="mono">{{ e.client }}</td>
                <td class="mono">{{ e.domain }}</td>
                <td><span class="badge" :class="'badge-'+e.action">{{ e.action }}</span></td>
                <td>{{ e.cache }}</td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </div>
  </div>
</template>
