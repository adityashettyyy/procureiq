import axios from "axios";

const BASE = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

export const api = axios.create({ baseURL: BASE });

// ── Types ────────────────────────────────────────────────────

export interface ParsedQuery {
  product?: string;
  grade?: string;
  quantity?: number;
  material?: string;
  search_string?: string;
}

export interface QuoteResult {
  id: string;
  supplier_url: string;
  supplier_name?: string;
  unit_price?: number;
  currency: string;
  price_per_unit_label?: string;
  moq?: number;
  shipping_cost?: number;
  shipping_days_min?: number;
  shipping_days_max?: number;
  availability?: string;
  product_url?: string;
  product_name?: string;
  confidence: "HIGH" | "MEDIUM" | "LOW";
  confidence_reason?: string;
  composite_score?: number;
  is_best_value: boolean;
  is_fastest: boolean;
  is_recommended: boolean;
  agent_steps?: string[];
  status: string;
  error_message?: string;
  completed_at?: string;
}

export interface QuoteJob {
  id: string;
  product_description: string;
  supplier_urls: string[];
  status: "PENDING" | "RUNNING" | "PARTIAL" | "COMPLETE" | "FAILED";
  total_suppliers: number;
  completed_suppliers: number;
  failed_suppliers: number;
  human_minutes_saved?: number;
  winner_explanation?: string[];
  parsed_query?: ParsedQuery;
  results: QuoteResult[];
  duration_seconds?: number;
  live_steps?: string[];
  created_at: string;
  completed_at?: string;
}

export interface Supplier {
  id: string;
  name: string;
  url: string;
  logo_url?: string;
  category?: string;
  is_active: boolean;
  is_verified: boolean;
  trust_score?: number;
  seller_count?: string;
  avg_response_time?: string;
}

export interface Metrics {
  total_jobs: number;
  successful_jobs: number;
  total_quotes_collected: number;
  total_hours_saved: number;
  total_minutes_saved: number;
}

export interface RFQDraft {
  id: string;
  subject: string;
  body: string;
  recipient_hint?: string;
}

// ── API calls ────────────────────────────────────────────────

export const createQuoteJob = async (
  product_description: string,
  supplier_urls: string[]
) => {
  const res = await api.post("/api/quotes", { product_description, supplier_urls });
  return res.data as { job_id: string; status: string; parsed_query: ParsedQuery };
};

export const getQuoteJob = async (jobId: string): Promise<QuoteJob> => {
  const res = await api.get(`/api/quotes/${jobId}`);
  return res.data;
};

export const getQuoteStatus = async (jobId: string) => {
  const res = await api.get(`/api/quotes/${jobId}/status`);
  return res.data;
};

export const listQuoteJobs = async () => {
  const res = await api.get("/api/quotes");
  return res.data as QuoteJob[];
};

export const generateRFQ = async (
  jobId: string,
  resultId: string
): Promise<RFQDraft> => {
  const res = await api.post(`/api/quotes/${jobId}/rfq-email`, {
    selected_result_id: resultId,
  });
  return res.data;
};

export const exportCSV = (jobId: string) => {
  window.open(`${BASE}/api/quotes/${jobId}/export`, "_blank");
};

export const listSuppliers = async (): Promise<Supplier[]> => {
  const res = await api.get("/api/suppliers");
  return res.data;
};

export const createSupplier = async (data: {
  name: string;
  url: string;
  category?: string;
}): Promise<Supplier> => {
  const res = await api.post("/api/suppliers", data);
  return res.data;
};

export const deleteSupplier = async (id: string) => {
  await api.delete(`/api/suppliers/${id}`);
};

export const getMetrics = async (): Promise<Metrics> => {
  const res = await api.get("/api/metrics/summary");
  return res.data;
};

export const getActiveAgents = async (): Promise<number> => {
  const res = await api.get("/api/metrics/active-agents");
  return res.data.active_agents;
};

// ── Helpers ──────────────────────────────────────────────────

export const formatPrice = (price?: number, currency = "USD") => {
  if (price == null) return "—";
  const sym = currency === "INR" ? "₹" : currency === "USD" ? "$" : currency + " ";
  return `${sym}${price.toFixed(2)}`;
};

export const formatLeadTime = (min?: number, max?: number) => {
  if (!min && !max) return "—";
  if (min === max || !max) return `${min || max} days`;
  return `${min}–${max} days`;
};

export const confidenceColor = (c: string) => {
  if (c === "HIGH") return "text-green-400 bg-green-400/10";
  if (c === "MEDIUM") return "text-yellow-400 bg-yellow-400/10";
  return "text-red-400 bg-red-400/10";
};

export const confidenceDot = (c: string) => {
  if (c === "HIGH") return "bg-green-400";
  if (c === "MEDIUM") return "bg-yellow-400";
  return "bg-red-400";
};

export const statusColor = (s: string) => {
  const map: Record<string, string> = {
    COMPLETE: "text-green-400",
    PARTIAL: "text-yellow-400",
    RUNNING: "text-blue-400",
    PENDING: "text-slate-400",
    FAILED: "text-red-400",
  };
  return map[s] || "text-slate-400";
};
