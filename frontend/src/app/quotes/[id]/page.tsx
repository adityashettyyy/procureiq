"use client";
import { useEffect, useState, useRef, useCallback } from "react";
import { useParams, useRouter } from "next/navigation";
import Link from "next/link";
import { Download, Mail, Plus, CheckCircle, AlertTriangle, Clock, Zap, ChevronRight, Bell } from "lucide-react";
import {
  getQuoteJob, generateRFQ, exportCSV,
  formatPrice, formatLeadTime, confidenceColor, confidenceDot,
  type QuoteJob, type QuoteResult, type RFQDraft
} from "@/lib/api";
import AppShell from "@/components/shared/AppShell";
import RFQModal from "@/components/quote/RFQModal";
import ParsedQueryBanner from "@/components/quote/ParsedQueryBanner";
import TimeSavedCounter from "@/components/quote/TimeSavedCounter";

const AGENT_MONOLOGUE: Record<string, string[]> = {
  start:   ["Initialising agent...", "Parsing product specification...", "Identifying search strategy..."],
  nav:     ["Navigating to supplier homepage...", "Waiting for page to load...", "Page loaded successfully"],
  search:  ["Located search interface", "Submitting product query...", "Evaluating search results..."],
  extract: ["Identified best matching product", "Opening product page...", "Extracting pricing table...", "Confirming availability status...", "Cross-referencing bulk discount tiers..."],
  done:    ["Extraction complete ✓", "Packaging results..."],
};

function getMonologueStep(index: number): string {
  const all = [...AGENT_MONOLOGUE.start, ...AGENT_MONOLOGUE.nav, ...AGENT_MONOLOGUE.search, ...AGENT_MONOLOGUE.extract, ...AGENT_MONOLOGUE.done];
  return all[index % all.length];
}

export default function QuoteResultsPage() {
  const { id } = useParams<{ id: string }>();
  const [job, setJob] = useState<QuoteJob | null>(null);
  const [visibleResults, setVisibleResults] = useState<QuoteResult[]>([]);
  const [steps, setSteps] = useState<string[]>([]);
  const [monologueStep, setMonologueStep] = useState(0);
  const [rfqModal, setRfqModal] = useState<{ result: QuoteResult } | null>(null);
  const [rfqDraft, setRfqDraft] = useState<RFQDraft | null>(null);
  const [rfqLoading, setRfqLoading] = useState(false);
  const [startTime] = useState(Date.now());
  const pollRef = useRef<ReturnType<typeof setInterval> | null>(null);
  const prevCompleted = useRef(0);
  const [notifications, setNotifications] = useState<string[]>([]);
  const [showNotifications, setShowNotifications] = useState(false);

  const pollJob = useCallback(async () => {
    try {
      const data = await getQuoteJob(id);
      setJob(data);
      if (data.live_steps?.length) setSteps(data.live_steps);

      // Staggered card reveal
      const newResults = data.results.filter(
        (r) => r.status !== "RUNNING" && !visibleResults.find((v) => v.id === r.id)
      );
      if (newResults.length > 0) {
        newResults.forEach((r, i) => {
          setTimeout(() => {
            setVisibleResults((prev) => {
              if (prev.find((p) => p.id === r.id)) return prev;
              return [...prev, r];
            });
            // Add notification for new quote
            if (r.status === "COMPLETE") {
              const supplier = r.supplier_name || new URL(r.supplier_url).hostname;
              setNotifications(prev => [`New quote from ${supplier}: $${r.unit_price}`, ...prev.slice(0, 4)]);
            }
          }, i * 2500);
        });
      }

      if (["COMPLETE", "PARTIAL", "FAILED"].includes(data.status)) {
        if (pollRef.current) clearInterval(pollRef.current);
        // Final reveal of any remaining results
        setTimeout(() => {
          setVisibleResults(data.results);
        }, data.results.length * 2500 + 500);
      }
    } catch (e) {
      console.error(e);
    }
  }, [id, visibleResults]);

  // Monologue ticker
  useEffect(() => {
    const t = setInterval(() => setMonologueStep((p) => p + 1), 4000);
    return () => clearInterval(t);
  }, []);

  // Polling
  useEffect(() => {
    pollJob();
    pollRef.current = setInterval(pollJob, 2500);
    return () => { if (pollRef.current) clearInterval(pollRef.current); };
  }, []);  // eslint-disable-line

  // Close notifications on click outside
  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      if (showNotifications && !(event.target as Element).closest('.notification-dropdown')) {
        setShowNotifications(false);
      }
    };
    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, [showNotifications]);

  const handleGenerateRFQ = async (result: QuoteResult) => {
    if (!job) return;
    setRfqModal({ result });
    setRfqLoading(true);
    try {
      const draft = await generateRFQ(job.id, result.id);
      setRfqDraft(draft);
    } catch (e) { console.error(e); }
    finally { setRfqLoading(false); }
  };

  const isRunning = job?.status === "RUNNING" || job?.status === "PENDING";
  const completed = job?.completed_suppliers ?? 0;
  const total = job?.total_suppliers ?? 3;
  const progress = total > 0 ? (completed / total) * 100 : 0;

  return (
    <AppShell>
      <div className="max-w-7xl mx-auto px-6 py-8">
        {/* Header */}
        <div className="flex items-start justify-between mb-6 gap-4 flex-wrap">
          <div>
            <div className="flex items-center gap-2 text-slate-400 text-sm mb-2">
              <Link href="/dashboard" className="hover:text-white transition-colors">Dashboard</Link>
              <ChevronRight className="w-3.5 h-3.5" />
              <span className="text-white">Quote Results</span>
            </div>
            <h1 className="text-xl font-bold text-white leading-snug max-w-2xl">
              {job?.product_description || "Loading..."}
            </h1>
          </div>
          <div className="flex items-center gap-3 shrink-0">
            {/* Notifications */}
            <div className="relative notification-dropdown">
              <button
                onClick={() => setShowNotifications(!showNotifications)}
                className="relative p-2 text-slate-400 hover:text-white transition-colors"
              >
                <Bell className="w-5 h-5" />
                {notifications.length > 0 && (
                  <span className="absolute -top-1 -right-1 bg-red-500 text-white text-xs rounded-full w-5 h-5 flex items-center justify-center">
                    {notifications.length}
                  </span>
                )}
              </button>
              {showNotifications && (
                <div className="absolute right-0 top-12 w-80 bg-brand-slate border border-slate-700 rounded-xl shadow-lg z-50">
                  <div className="p-3 border-b border-slate-700">
                    <h4 className="font-semibold text-white">Notifications</h4>
                  </div>
                  <div className="max-h-64 overflow-y-auto">
                    {notifications.length === 0 ? (
                      <div className="p-4 text-center text-slate-500 text-sm">
                        No new notifications
                      </div>
                    ) : (
                      notifications.map((note, i) => (
                        <div key={i} className="p-3 border-b border-slate-800 last:border-b-0 text-sm text-slate-300">
                          {note}
                        </div>
                      ))
                    )}
                  </div>
                  {notifications.length > 0 && (
                    <div className="p-3 border-t border-slate-700">
                      <button
                        onClick={() => setNotifications([])}
                        className="text-xs text-slate-400 hover:text-white"
                      >
                        Clear all
                      </button>
                    </div>
                  )}
                </div>
              )}
            </div>
            {job && !isRunning && (
              <button
                onClick={() => exportCSV(job.id)}
                className="flex items-center gap-2 border border-slate-700 text-slate-300 hover:text-white px-4 py-2 rounded-lg text-sm transition-colors"
              >
                <Download className="w-4 h-4" /> Export CSV
              </button>
            )}
            <Link
              href="/quotes/new"
              className="flex items-center gap-2 bg-green-500 text-black font-semibold px-4 py-2 rounded-lg text-sm hover:bg-green-400 transition-colors"
            >
              <Plus className="w-4 h-4" /> New Hunt
            </Link>
          </div>
        </div>

        {/* Parsed query banner */}
        {job?.parsed_query?.search_string && (
          <ParsedQueryBanner query={job.parsed_query} />
        )}

        {/* Progress bar + time saved */}
        <div className="grid md:grid-cols-2 gap-4 mb-8">
          {/* Progress */}
          <div className="bg-brand-slate border border-slate-700 rounded-xl p-4">
            <div className="flex items-center justify-between mb-3">
              <span className="text-sm text-slate-400">
                {isRunning ? "Agents working..." : `${completed} of ${total} suppliers checked`}
              </span>
              <span className="text-sm font-semibold">
                {isRunning
                  ? <span className="text-blue-400 flex items-center gap-1"><span className="w-2 h-2 bg-blue-400 rounded-full animate-pulse" />Running</span>
                  : job?.status === "COMPLETE"
                  ? <span className="text-green-400 flex items-center gap-1"><CheckCircle className="w-3.5 h-3.5" />Complete</span>
                  : <span className="text-yellow-400">{job?.status}</span>
                }
              </span>
            </div>
            <div className="h-2 bg-slate-700 rounded-full overflow-hidden">
              <div
                className="h-full bg-green-400 rounded-full transition-all duration-700"
                style={{ width: `${progress}%` }}
              />
            </div>
            <div className="text-xs text-slate-500 mt-2">{completed}/{total} suppliers · {total - completed} remaining</div>
          </div>

          {/* Time saved counter */}
          <TimeSavedCounter startTime={startTime} isRunning={isRunning} minutesSaved={job?.human_minutes_saved} />
        </div>

        <div className="grid lg:grid-cols-3 gap-6">
          {/* Quote cards */}
          <div className="lg:col-span-2 space-y-4">
            {/* Running placeholders */}
            {isRunning && Array.from({ length: total - visibleResults.length }).map((_, i) => (
              <div key={`skeleton-${i}`} className="bg-brand-slate border border-slate-700 rounded-2xl p-6 animate-pulse">
                <div className="flex items-center gap-3 mb-4">
                  <div className="w-8 h-8 bg-slate-700 rounded-lg skeleton" />
                  <div className="h-4 bg-slate-700 rounded w-32 skeleton" />
                  <div className="ml-auto flex items-center gap-1.5 text-blue-400 text-xs">
                    <span className="w-2 h-2 bg-blue-400 rounded-full animate-pulse" />
                    Agent searching...
                  </div>
                </div>
                <div className="h-8 bg-slate-700 rounded w-24 mb-3 skeleton" />
                <div className="space-y-2">
                  {[40, 60, 50].map((w, j) => (
                    <div key={j} className={`h-3 bg-slate-700 rounded skeleton`} style={{ width: `${w}%` }} />
                  ))}
                </div>
                <div className="mt-4 text-xs text-slate-500 typewriter">{getMonologueStep(monologueStep + i * 3)}</div>
              </div>
            ))}

            {/* Result cards */}
            {visibleResults.map((result) => (
              <QuoteCard key={result.id} result={result} onRFQ={() => handleGenerateRFQ(result)} />
            ))}
          </div>

          {/* Right sidebar — activity feed + winner explanation */}
          <div className="space-y-4">
            {/* Winner explanation */}
            {job?.winner_explanation && (
              <div className="bg-green-400/5 border border-green-400/20 rounded-xl p-4">
                <h3 className="text-sm font-semibold text-green-400 mb-3 flex items-center gap-2">
                  <CheckCircle className="w-4 h-4" /> Why we recommend this vendor
                </h3>
                <ul className="space-y-2">
                  {job.winner_explanation.map((bullet, i) => (
                    <li key={i} className="text-sm text-slate-300 leading-relaxed">{bullet}</li>
                  ))}
                </ul>
              </div>
            )}

            {/* Live activity feed */}
            <div className="bg-brand-slate border border-slate-700 rounded-xl overflow-hidden">
              <div className="px-4 py-3 border-b border-slate-700 flex items-center gap-2">
                <span className={`w-2 h-2 rounded-full ${isRunning ? "bg-blue-400 animate-pulse" : "bg-green-400"}`} />
                <span className="text-xs font-semibold uppercase tracking-wide text-slate-400">Agent Activity</span>
              </div>
              <div className="p-3 h-64 overflow-y-auto space-y-1.5 font-mono text-xs">
                {steps.length === 0 ? (
                  <p className="text-slate-600 italic">Waiting for agent activity...</p>
                ) : (
                  steps.slice(-30).map((step, i) => (
                    <div key={i} className={`${i === steps.length - 1 && isRunning ? "text-blue-300 typewriter" : "text-slate-400"}`}>
                      → {step}
                    </div>
                  ))
                )}
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* RFQ Modal */}
      {rfqModal && (
        <RFQModal
          result={rfqModal.result}
          draft={rfqDraft}
          loading={rfqLoading}
          onClose={() => { setRfqModal(null); setRfqDraft(null); }}
        />
      )}
    </AppShell>
  );
}

// ── QuoteCard component ──────────────────────────────────────

function QuoteCard({ result, onRFQ }: { result: QuoteResult; onRFQ: () => void }) {
  if (result.status === "FAILED" || result.status === "BLOCKED" || result.status === "NOT_FOUND") {
    return (
      <div className="bg-brand-slate border border-slate-700 rounded-2xl p-6 opacity-60 animate-fade-in">
        <div className="flex items-center gap-2 text-slate-400">
          <AlertTriangle className="w-5 h-5 text-yellow-500" />
          <span className="font-semibold">{result.supplier_name || result.supplier_url}</span>
        </div>
        <p className="text-sm text-slate-500 mt-2">Supplier unavailable — {result.error_message || result.status}</p>
      </div>
    );
  }

  return (
    <div className={`relative bg-brand-slate border rounded-2xl p-6 animate-flip-in transition-all ${
      result.is_recommended ? "border-green-400/50 shadow-lg shadow-green-400/5" : "border-slate-700"
    }`}>
      {/* Winner ribbon */}
      {result.is_recommended && (
        <div className="absolute -top-3 left-6">
          <span className="bg-green-400 text-black text-xs font-bold px-3 py-1 rounded-full">
            ✓ RECOMMENDED
          </span>
        </div>
      )}
      {result.is_best_value && !result.is_recommended && (
        <div className="absolute -top-3 left-6">
          <span className="bg-blue-400 text-black text-xs font-bold px-3 py-1 rounded-full">
            BEST VALUE
          </span>
        </div>
      )}
      {result.is_fastest && !result.is_recommended && !result.is_best_value && (
        <div className="absolute -top-3 left-6">
          <span className="bg-purple-400 text-black text-xs font-bold px-3 py-1 rounded-full">
            ⚡ FASTEST
          </span>
        </div>
      )}

      {/* Header */}
      <div className="flex items-start justify-between mb-4 mt-1">
        <div>
          <h3 className="font-bold text-white flex items-center gap-2">
            {result.supplier_name || new URL(result.supplier_url).hostname}
            {result.is_verified && (
              <span className="bg-blue-500/20 text-blue-400 text-xs px-2 py-0.5 rounded-full border border-blue-400/30">
                ✓ Verified
              </span>
            )}
            {result.trust_score && result.trust_score >= 90 && (
              <span className="bg-green-500/20 text-green-400 text-xs px-2 py-0.5 rounded-full border border-green-400/30">
                🛡️ Trusted ({result.trust_score}%)
              </span>
            )}
          </h3>
          {result.product_name && <p className="text-slate-400 text-xs mt-0.5 max-w-xs truncate">{result.product_name}</p>}
        </div>
        <div className={`flex items-center gap-1.5 text-xs px-2.5 py-1 rounded-full font-semibold ${confidenceColor(result.confidence)}`}>
          <span className={`w-1.5 h-1.5 rounded-full ${confidenceDot(result.confidence)}`} />
          {result.confidence}
        </div>
      </div>

      {/* Price — THE most important number */}
      <div className="mb-4">
        <div className="flex items-baseline gap-2">
          <span className="text-4xl font-black text-white">
            {formatPrice(result.unit_price, result.currency)}
          </span>
          {result.price_per_unit_label && (
            <span className="text-slate-400 text-sm">/ {result.price_per_unit_label}</span>
          )}
        </div>
      </div>

      {/* Details grid */}
      <div className="grid grid-cols-2 gap-3 mb-5 text-sm">
        <div>
          <p className="text-slate-500 text-xs mb-0.5">MOQ</p>
          <p className="font-semibold">{result.moq ? `${result.moq} units` : "—"}</p>
        </div>
        <div>
          <p className="text-slate-500 text-xs mb-0.5">Shipping</p>
          <p className="font-semibold">{result.shipping_cost != null ? formatPrice(result.shipping_cost, result.currency) : "—"}</p>
        </div>
        <div>
          <p className="text-slate-500 text-xs mb-0.5">Lead Time</p>
          <p className="font-semibold flex items-center gap-1">
            <Clock className="w-3 h-3 text-slate-400" />
            {formatLeadTime(result.shipping_days_min, result.shipping_days_max)}
          </p>
        </div>
        <div>
          <p className="text-slate-500 text-xs mb-0.5">Availability</p>
          <p className={`font-semibold text-xs ${result.availability?.toLowerCase().includes("stock") ? "text-green-400" : "text-yellow-400"}`}>
            {result.availability || "—"}
          </p>
        </div>
      </div>

      {/* Confidence reason tooltip-style */}
      {result.confidence_reason && (
        <p className="text-xs text-slate-500 italic border-t border-slate-700 pt-3 mb-4">
          "{result.confidence_reason}"
        </p>
      )}

      {/* Actions */}
      <div className="flex items-center gap-2">
        {result.product_url && (
          <a
            href={result.product_url}
            target="_blank"
            rel="noopener noreferrer"
            className="flex-1 text-center border border-slate-700 text-slate-300 hover:text-white text-sm py-2 rounded-lg transition-colors"
          >
            View Product
          </a>
        )}
        <button
          onClick={onRFQ}
          className="flex-1 flex items-center justify-center gap-1.5 bg-green-500/10 border border-green-400/30 text-green-400 hover:bg-green-500/20 text-sm py-2 rounded-lg transition-colors font-semibold"
        >
          <Mail className="w-3.5 h-3.5" />
          Get RFQ Email
        </button>
      </div>
    </div>
  );
}
