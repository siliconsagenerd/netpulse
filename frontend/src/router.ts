import { createRouter, createWebHashHistory } from "vue-router";

export default createRouter({
  history: createWebHashHistory(),
  routes: [
    { path: "/", component: () => import("./views/Overview.vue") },
    { path: "/diagnostics", alias: ["/diagnostic"], component: () => import("./views/Diagnostics.vue") },
    { path: "/cache", alias: ["/cache-lab", "/cachelab"], component: () => import("./views/CacheLab.vue") },
    { path: "/reports", component: () => import("./views/Reports.vue") },
    { path: "/about", component: () => import("./views/About.vue") },
    { path: "/:pathMatch(.*)*", redirect: "/" },
  ],
  scrollBehavior() { return { top: 0 }; },
});
