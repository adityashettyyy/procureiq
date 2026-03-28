"use client";
import { useEffect, useState } from "react";
import Link from "next/link";
import { Plus, Download, ExternalLink, Clock, TrendingDown, CheckCircle, Zap } from "lucide-react";
import { listQuoteJobs, getMetrics, exportCSV, formatPrice, statusColor, type QuoteJob, type Metrics } from "@/lib/api";
import AppShell from "@/components/shared/AppShell";

export default function DashboardPage() {
  const [jobs, setJobs] = useState<QuoteJob[]>([]);
  const [metrics, setMetrics] = useState<Metrics | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    Promise.all([listQuoteJobs(), getMetrics()])
      .then(([j, m]) => { setJobs(j); setMetrics(m); })
      .catch(console.error)
      .finally(() => setLoading(false));
  }, []);

  return (
    <AppShell>
      <div className="max-w-6xl mx-auto px-6 py-8">
        {/* Header */}
        <div className="flex items-center justify-between mb-8">
          <div>
            <h1 className="text-2xl font-bold">Dashboard</h1>
            <p className="text-slate-400 text-sm mt-1">Your procurement intelligence hub</p>
          </div>
          <Link
            href="/quotes/new"
            className="flex items-center gap-2 bg-brand-green text-black font-bold px-5 py-2.5 rounded-xl hover:bg-green-400 transition-colors"
          >
            <Plus className="w-4 h-4" />
            New Quote Hunt
          </Link>
        </div>

        {/* Stat cards */}
        {metrics && (
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-8">
            {[
              { label: "Total Hunts", value: metrics.total_jobs, icon: Zap, color: "text-blue-400" },
              { label: "Hours Saved", value: `${metrics.total_hours_saved}h`, icon: Clock, color: "text-green-400" },
              { label: "Quotes Collected", value: metrics.total_quotes_collected, icon: CheckCircle, color: "text-purple-400" },
              { label: "Success Rate", value: metrics.total_jobs ? `${Math.round(metrics.successful_jobs / metrics.total_jobs * 100)}%` : "—", icon: TrendingDown, color: "text-yellow-400" },
            ].map((s) => (
              <div key={s.label} className="bg-brand-slate border border-slate-700 rounded-xl p-4">
                <div className="flex items-center gap-2 mb-2">
                  <s.icon className={`w-4 h-4 ${s.color}`} />
                  <span className="text-xs text-slate-500 uppercase tracking-wide">{s.label}</span>
                </div>
                <div className="text-2xl font-black">{s.value}</div>
              </div>
            ))}
          </div>
        )}

        {/* Jobs table */}
        <div className="bg-brand-slate border border-slate-700 rounded-xl overflow-hidden">
          <div className="px-6 py-4 border-b border-slate-700">
            <h2 className="font-semibold">Recent Quote Hunts</h2>
          </div>

          {loading ? (
            <div className="p-8 text-center text-slate-500">Loading...</div>
          ) : jobs.length === 0 ? (
            <div className="p-12 text-center">
              <Zap className="w-10 h-10 text-slate-600 mx-auto mb-4" />
              <p className="text-slate-400 mb-4">No quote hunts yet</p>
              <Link href="/quotes/new" className="text-green-400 font-semibold hover:underline">
                Run your first quote hunt →
              </Link>
            </div>
          ) : (
            <div className="overflow-x-auto">
              <table className="w-full text-sm">
                <thead>
                  <tr className="border-b border-slate-700 text-slate-500 text-xs uppercase tracking-wide">
                    <th className="px-6 py-3 text-left">Product</th>
                    <th className="px-6 py-3 text-left">Status</th>
                    <th className="px-6 py-3 text-left">Best Price</th>
                    <th className="px-6 py-3 text-left">Saved</th>
                    <th className="px-6 py-3 text-left">Time</th>
                    <th className="px-6 py-3 text-left">Actions</th>
                  </tr>
                </thead>
                <tbody>
                  {jobs.map((job) => (
                    <tr key={job.id} className="border-b border-slate-800 hover:bg-slate-800/30 transition-colors">
                      <td className="px-6 py-4">
                        <div className="font-medium text-white max-w-xs truncate">{job.product_description}</div>
                        <div className="text-slate-500 text-xs mt-0.5">
                          {job.completed_suppliers}/{job.total_suppliers} suppliers
                        </div>
                      </td>
                      <td className="px-6 py-4">
                        <span className={`font-semibold text-xs ${statusColor(job.status)}`}>
                          {job.status}
                        </span>
                      </td>
                      <td className="px-6 py-4 font-mono font-bold text-green-400">
                        {formatPrice(job.best_price as any, job.best_price_currency as any)}
                        {job.best_supplier_name && (
                          <div className="text-slate-500 text-xs font-normal mt-0.5">{job.best_supplier_name}</div>
                        )}
                      </td>
                      <td className="px-6 py-4 text-green-400 font-semibold">
                        {job.human_minutes_saved ? `${Math.floor(job.human_minutes_saved / 60)}h ${job.human_minutes_saved % 60}m` : "—"}
                      </td>
                      <td className="px-6 py-4 text-slate-400">
                        {job.duration_seconds ? `${Math.round(job.duration_seconds)}s` : "—"}
                      </td>
                      <td className="px-6 py-4">
                        <div className="flex items-center gap-2">
                          <Link
                            href={`/quotes/${job.id}`}
                            className="flex items-center gap-1 text-blue-400 hover:text-blue-300 text-xs"
                          >
                            <ExternalLink className="w-3 h-3" />
                            View
                          </Link>
                          {job.status !== "PENDING" && job.status !== "RUNNING" && (
                            <button
                              onClick={() => exportCSV(job.id)}
                              className="flex items-center gap-1 text-slate-400 hover:text-white text-xs"
                            >
                              <Download className="w-3 h-3" />
                              CSV
                            </button>
                          )}
                        </div>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </div>
      </div>
    </AppShell>
  );
}
