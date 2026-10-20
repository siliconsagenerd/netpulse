<script setup lang="ts">
import { ref, onMounted } from "vue";
import { useI18n } from "./i18n";
import { RouterView, RouterLink } from "vue-router";

const { locale, t, setLocale } = useI18n();
const theme = ref(localStorage.getItem("np_theme") || "light");
const online = ref(navigator.onLine);

onMounted(() => {
  document.documentElement.setAttribute("data-theme", theme.value);
  window.addEventListener("online", () => (online.value = true));
  window.addEventListener("offline", () => (online.value = false));
});
function toggleTheme() {
  theme.value = theme.value === "light" ? "dark" : "light";
  document.documentElement.setAttribute("data-theme", theme.value);
  localStorage.setItem("np_theme", theme.value);
}
</script>

<template>
  <div class="app">
    <a href="#main-content" class="skip-link">Skip to content</a>
    <header class="topbar">
      <div class="brand">{{ t("app") }}</div>
      <nav class="nav">
        <RouterLink to="/">{{ t("nav.overview") }}</RouterLink>
        <RouterLink to="/diagnostics">{{ t("nav.diagnostics") }}</RouterLink>
        <RouterLink to="/cache">{{ t("nav.cache") }}</RouterLink>
        <RouterLink to="/reports">{{ t("nav.reports") }}</RouterLink>
        <RouterLink to="/about">{{ t("nav.about") }}</RouterLink>
      </nav>
      <div class="controls">
        <select :value="locale" @change="setLocale(($event.target as HTMLSelectElement).value)" aria-label="language">
          <option value="de">DE</option>
          <option value="en">EN</option>
        </select>
        <button class="iconbtn" @click="toggleTheme" :aria-label="theme === 'light' ? 'Switch to dark theme' : 'Switch to light theme'">
  <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">
    <path v-if="theme==='light'" d="M21 12.79A9 9 0 1 1 11.21 3 7 7 0 0 0 21 12.79z"/>
    <template v-else>
      <circle cx="12" cy="12" r="5"/>
      <line x1="12" y1="1" x2="12" y2="3"/>
      <line x1="12" y1="21" x2="12" y2="23"/>
      <line x1="4.22" y1="4.22" x2="5.64" y2="5.64"/>
      <line x1="18.36" y1="18.36" x2="19.78" y2="19.78"/>
      <line x1="1" y1="12" x2="3" y2="12"/>
      <line x1="21" y1="12" x2="23" y2="12"/>
      <line x1="4.22" y1="19.78" x2="5.64" y2="18.36"/>
      <line x1="18.36" y1="5.64" x2="19.78" y2="4.22"/>
    </template>
  </svg>
</button>
      </div>
    </header>
    <div v-if="!online" class="offline-banner" role="status">{{ t("offline") || "You are offline. Changes may not be saved." }}</div>
    <main id="main-content" class="main" tabindex="-1">
      <RouterView />
    </main>
    <footer class="footer">NetPulse · simulated demo · v0.1.0</footer>
  </div>
</template>

<style>
:root {
  --bg: #f5f5f7; --surface: #ffffff; --surface-2: #fafafa;
  --text: #1d1d1f; --muted: #6e6e73; --border: #d2d2d7;
  --accent: #0071e3; --accent-2: #0066cc;
  --danger: #d70015; --success: #1d7a3a; --warn: #b25000;
  --mono: "SF Mono", ui-monospace, Menlo, monospace;
  --radius: 12px; --shadow: 0 1px 3px rgba(0,0,0,.08);
}
[data-theme="dark"] {
  --bg: #0b0b0c; --surface: #1c1c1e; --surface-2: #2c2c2e;
  --text: #f5f5f7; --muted: #a1a1a6; --border: #3a3a3c;
  --accent: #2997ff; --accent-2: #0a84ff;
  --danger: #ff453a; --success: #30d158; --warn: #ff9f0a;
  --shadow: 0 1px 3px rgba(0,0,0,.4);
}
* { box-sizing: border-box; }
html, body { margin: 0; padding: 0; }
body { font-family: -apple-system, BlinkMacSystemFont, "SF Pro Text", "Segoe UI", Roboto, sans-serif; background: var(--bg); color: var(--text); -webkit-font-smoothing: antialiased; transition: background .3s ease, color .3s ease; }
@media (prefers-reduced-motion: reduce) {
  *, *::before, *::after { transition: none !important; animation: none !important; }
}
.app { min-height: 100vh; display: flex; flex-direction: column; }
.topbar { display: flex; align-items: center; gap: 16px; padding: 12px 20px; background: color-mix(in srgb, var(--surface) 75%, transparent); backdrop-filter: saturate(180%) blur(20px); -webkit-backdrop-filter: saturate(180%) blur(20px); border-bottom: 1px solid var(--border); position: sticky; top: 0; z-index: 10; flex-wrap: wrap; }
.brand { font-weight: 700; font-size: 18px; letter-spacing: -0.3px; }
.nav { display: flex; gap: 4px; flex: 1; flex-wrap: wrap; }
@media (max-width: 480px) { .nav { flex-wrap: nowrap; overflow-x: auto; -webkit-overflow-scrolling: touch; } .topbar { gap: 8px; } .brand { font-size: 15px; } }
.nav a { padding: 6px 10px; border-radius: 8px; text-decoration: none; color: var(--text); font-size: 14px; }
.nav a.router-link-active { background: var(--accent-bg, rgba(0,113,227,.1)); color: var(--accent); font-weight: 600; }
.controls { display: flex; gap: 8px; align-items: center; }
.controls select { background: var(--surface-2); color: var(--text); border: 1px solid var(--border); border-radius: 8px; padding: 4px 8px; }
.iconbtn { background: var(--surface-2); border: 1px solid var(--border); border-radius: 8px; padding: 4px 8px; cursor: pointer; color: var(--text); }
.skip-link { position: absolute; left: -9999px; top: 0; background: var(--accent); color: #fff; padding: 8px 12px; z-index: 100; border-radius: 0 0 8px 0; font-size: 13px; }
.skip-link:focus { left: 0; }
.main { flex: 1; padding: 24px 20px; max-width: 1100px; margin: 0 auto; width: 100%; }
.main:focus { outline: none; }
.footer { padding: 16px 20px; text-align: center; color: var(--muted); font-size: 12px; border-top: 1px solid var(--border); }
.card { background: var(--surface); border: 1px solid var(--border); border-radius: var(--radius); padding: 16px; box-shadow: var(--shadow); }
.grid { display: grid; gap: 16px; }
.grid-2 { grid-template-columns: repeat(auto-fit, minmax(240px, 1fr)); }
.grid-3 { grid-template-columns: repeat(auto-fit, minmax(180px, 1fr)); }
.kpi { font-size: 28px; font-weight: 700; letter-spacing: -0.5px; }
.kpi-label { font-size: 12px; color: var(--muted); text-transform: uppercase; letter-spacing: 0.5px; }
.btn { background: var(--accent); color: #fff; border: none; border-radius: 8px; padding: 8px 14px; min-height: 36px; cursor: pointer; font-weight: 600; font-size: 14px; transition: transform .12s cubic-bezier(.2,.8,.2,1), background .2s ease, box-shadow .2s ease; }
.btn:hover { transform: translateY(-1px); box-shadow: 0 2px 6px rgba(0,0,0,.12); }
.btn:active { transform: translateY(0) scale(.97); }
.btn:focus-visible { outline: 2px solid var(--accent); outline-offset: 2px; }
.btn:disabled { opacity: 0.5; cursor: not-allowed; transform: none; box-shadow: none; }
.card { background: var(--surface); border: 1px solid var(--border); border-radius: var(--radius); padding: 16px; box-shadow: var(--shadow); transition: box-shadow .25s ease, transform .25s cubic-bezier(.2,.8,.2,1); }
.card:hover { box-shadow: 0 8px 24px rgba(0,0,0,.1); transform: translateY(-1px); }
.nav a { padding: 6px 10px; border-radius: 8px; text-decoration: none; color: var(--text); font-size: 14px; transition: background .15s ease, color .15s ease; }
.nav a:hover { background: var(--surface-2); }
.select, .input { transition: border-color .15s ease, box-shadow .15s ease; }
.input:focus { border-color: var(--accent); box-shadow: 0 0 0 3px rgba(0,113,227,.15); outline: none; }
.badge { display: inline-block; padding: 2px 8px; border-radius: 6px; font-size: 11px; font-weight: 600; transition: transform .12s ease; }
.btn-secondary { background: var(--surface-2); color: var(--text); border: 1px solid var(--border); }
.btn-danger { background: var(--danger); color: #fff; }
.input { background: var(--surface-2); color: var(--text); border: 1px solid var(--border); border-radius: 8px; padding: 8px 10px; font-size: 14px; width: 100%; }
.table { width: 100%; border-collapse: collapse; font-size: 13px; }
.table th, .table td { padding: 8px 10px; border-bottom: 1px solid var(--border); text-align: left; }
.table th { color: var(--muted); font-weight: 600; font-size: 12px; text-transform: uppercase; }
.table tbody tr { transition: background .15s ease; }
.table tbody tr:hover { background: var(--surface-2); }
.mono { font-family: var(--mono); font-size: 12px; }
.badge { display: inline-block; padding: 2px 8px; border-radius: 6px; font-size: 11px; font-weight: 600; }
.badge-allow { background: rgba(29,122,58,.15); color: var(--success); }
.badge-block { background: rgba(215,0,21,.15); color: var(--danger); }
.badge-rate_limit { background: rgba(178,80,0,.15); color: var(--warn); }
.badge-route { background: rgba(0,113,227,.15); color: var(--accent); }
.simulated-tag { font-size: 10px; color: var(--muted); font-style: italic; }
.empty { color: var(--muted); padding: 24px; text-align: center; }
@media (max-width: 375px) {
  .main { padding: 16px 12px; }
  .topbar { padding: 10px 12px; }
  .kpi { font-size: 22px; }
}
</style>
