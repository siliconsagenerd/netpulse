<script setup lang="ts">
import { ref, computed, onMounted } from "vue";
import { useI18n } from "../i18n";
import { api } from "../services/api";
import type { Run, Dashboard } from "../types";

const { t } = useI18n();
const runs = ref<Run[]>([]);
const selected = ref("");
const dash = ref<Dashboard | null>(null);
const startSec = ref(0);
const endSec = ref(0);

const filteredSeries = computed(() => {
  const s = dash.value?.cache_series ?? [];
  if (!s.length) return [];
  const lo = startSec.value;
  const hi = endSec.value > 0 ? endSec.value : Infinity;
  return s.filter((p: any) => p.t >= lo && p.t <= hi);
});

async function load() {
  runs.value = await api.runs();
  if (runs.value.length && !selected.value) selected.value = runs.value[0].id;
  await refresh();
}
async function refresh() {
  if (!selected.value) return;
  dash.value = await api.dashboard(selected.value);
  const s = dash.value?.cache_series ?? [];
  startSec.value = s.length ? s[0].t : 0;
  endSec.value = s.length ? s[s.length - 1].t : 0;
}
onMounted(load);
</script>

<template>
  <div>
    <h1>{{ t("cache.title") }}</h1>
    <p class="simulated-tag">{{ t("cache.desc") }}</p>
    <div class="card" style="margin-bottom:16px">
      <label class="kpi-label">Run</label>
      <select class="input" style="width:auto" v-model="selected" @change="refresh">
        <option v-for="r in runs" :key="r.id" :value="r.id">{{ r.id.slice(0,8) }} (seed {{ r.seed }})</option>
      </select>
    </div>
    <div v-if="dash" class="card" style="margin-bottom:16px">
      <label class="kpi-label">Time window (seconds)</label>
      <div style="display:flex; gap:12px; align-items:center; margin-top:6px">
        <input class="input" type="number" v-model.number="startSec" style="width:100px" />
        <span>to</span>
        <input class="input" type="number" v-model.number="endSec" style="width:100px" />
      </div>
    </div>
    <div v-if="!runs.length" class="card" style="margin-bottom:16px">
      <div class="empty">No runs yet. Run a simulation on Diagnostics first.</div>
    </div>
    <div v-if="dash" class="grid grid-3" style="margin-bottom:16px">
      <div class="card"><div class="kpi-label">{{ t("cache.hitRatio") }}</div><div class="kpi">{{ ((dash.summary?.cache_hit_ratio ?? 0)*100).toFixed(1) }}%</div></div>
      <div class="card"><div class="kpi-label">{{ t("cache.finalSize") }}</div><div class="kpi">{{ dash.summary?.cache_final_size ?? 0 }}</div></div>
      <div class="card"><div class="kpi-label">Events</div><div class="kpi">{{ filteredSeries.length }}</div></div>
    </div>
    <div v-if="filteredSeries.length" class="card">
      <h3>{{ t("cache.series") }}</h3>
      <svg viewBox="0 0 400 120" width="100%" height="120" preserveAspectRatio="none">
        <polyline :points="filteredSeries.map((p:any,i:number)=> (i/(((filteredSeries.length ?? 1)-1)||1)*400)+','+(120-p.ratio*100)).join(' ')" fill="none" stroke="var(--accent)" stroke-width="2" />
      </svg>
    </div>
  </div>
</template>
