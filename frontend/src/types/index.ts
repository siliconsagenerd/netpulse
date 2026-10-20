export interface Client { id: string; name: string; ip: string; group: string }
export interface Domain { id: string; name: string; category: string }
export interface Rule {
  id: string; name: string; priority: number; enabled: boolean;
  match_client: string; match_domain: string; action: string;
  rate_limit_per_min?: number | null; route_to?: string | null; reason?: string | null;
}
export interface Run {
  id: string; seed: number; duration_seconds: number; request_rate: number;
  cache_ttl: number; cache_capacity: number; cache_policy: string; status: string;
  started_at: string; completed_at?: string | null; summary?: any;
}
export interface Event {
  id: string; run_id: string; ts: number; client: string; domain: string;
  action: string; reason?: string | null; matched_rule?: string | null;
  cache: string; status_code: number; latency_ms: number;
}
export interface Dashboard {
  run_id: string | null; summary: any;
  events_over_time: { t: number; count: number }[];
  actions: Record<string, number>;
  cache_series: { t: number; ratio: number }[];
  top_clients: Record<string, number>;
  top_domains: Record<string, number>;
}
export interface Report {
  run_id: string; timestamp: string; build_version: string;
  scenario: any; summary: any; rules: Rule[]; assertions: { name: string; passed: boolean }[];
  limitations: string[]; events_sample: Event[]; total_events: number;
}
