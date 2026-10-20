const BASE = (import.meta.env.VITE_API_BASE as string) || "/api";

async function req(path: string, opts: RequestInit = {}) {
  const r = await fetch(BASE + path, { credentials: "include", headers: { "Content-Type": "application/json" }, ...opts });
  if (!r.ok) throw new Error(`${r.status} ${r.statusText}`);
  return r.json();
}

export const api = {
  health: () => req("/health"),
  clients: () => req("/clients"),
  domains: () => req("/domains"),
  rules: () => req("/rules"),
  createRule: (b: any) => req("/rules", { method: "POST", body: JSON.stringify(b) }),
  updateRule: (id: string, b: any) => req(`/rules/${id}`, { method: "PUT", body: JSON.stringify(b) }),
  deleteRule: (id: string) => req(`/rules/${id}`, { method: "DELETE" }),
  toggleRule: (id: string) => req(`/rules/${id}/toggle`, { method: "PATCH" }),
  simulate: (b: any) => req("/simulate", { method: "POST", body: JSON.stringify(b) }),
  runs: () => req("/runs"),
  run: (id: string) => req(`/runs/${id}`),
  events: (id: string, params: Record<string, any> = {}) => {
    const q = new URLSearchParams();
    Object.entries(params).forEach(([k, v]) => { if (v !== "" && v != null) q.set(k, String(v)); });
    const qs = q.toString();
    return req(`/runs/${id}/events${qs ? "?" + qs : ""}`);
  },
  dashboard: (id?: string) => req(`/dashboard${id ? `?run_id=${id}` : ""}`),
  report: (id: string) => req(`/runs/${id}/report`),
};
