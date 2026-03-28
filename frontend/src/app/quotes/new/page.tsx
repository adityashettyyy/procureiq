"use client";
import { useState } from "react";
import { useRouter } from "next/navigation";
import { Plus, Trash2, Zap, Info } from "lucide-react";
import { createQuoteJob } from "@/lib/api";
import AppShell from "@/components/shared/AppShell";

const DEFAULT_SUPPLIERS = [
  { name: "IndiaMART", url: "https://www.indiamart.com" },
  { name: "Amazon Business", url: "https://www.amazon.in" },
  { name: "Alibaba", url: "https://www.alibaba.com" },
  { name: "TradeIndia", url: "https://www.tradeindia.com" },
];

const EXAMPLE_QUERIES = [
  "500 units M8 zinc-plated hex bolts grade 8.8",
  "A4 copy paper 80gsm 500 sheets — 10 reams",
  "USB-C to USB-A cable 1m braided — 20 units",
  "Office ergonomic chair with lumbar support — 5 units",
];

export default function NewQuotePage() {
  const router = useRouter();
  const [description, setDescription] = useState("");
  const [supplierUrls, setSupplierUrls] = useState(["", "", ""]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  const updateUrl = (i: number, val: string) => {
    const updated = [...supplierUrls];
    updated[i] = val;
    setSupplierUrls(updated);
  };

  const usePreset = (url: string, i: number) => {
    const updated = [...supplierUrls];
    updated[i] = url;
    setSupplierUrls(updated);
  };

  const handleSubmit = async () => {
    const validUrls = supplierUrls.filter((u) => u.trim());
    if (!description.trim()) { setError("Please describe what you need to buy."); return; }
    if (validUrls.length === 0) { setError("Add at least one supplier URL."); return; }
    setError("");
    setLoading(true);
    try {
      const res = await createQuoteJob(description.trim(), validUrls);
      router.push(`/quotes/${res.job_id}`);
    } catch (e: any) {
      setError(e?.response?.data?.detail || "Something went wrong. Please try again.");
      setLoading(false);
    }
  };

  return (
    <AppShell>
      <div className="max-w-2xl mx-auto px-6 py-10">
        <div className="mb-8">
          <h1 className="text-2xl font-bold mb-1">New Quote Hunt</h1>
          <p className="text-slate-400 text-sm">
            Describe what you need. We'll send agents to find the best prices.
          </p>
        </div>

        {/* Product description */}
        <div className="mb-6">
          <label className="block text-sm font-semibold mb-2">
            What do you need to buy?
          </label>
          <textarea
            rows={3}
            value={description}
            onChange={(e) => setDescription(e.target.value)}
            placeholder="e.g. 500 units M8 zinc-plated hex bolts, grade 8.8"
            className="w-full bg-brand-slate border border-slate-700 rounded-xl px-4 py-3 text-white placeholder-slate-500 focus:outline-none focus:border-green-500 resize-none text-sm"
          />
          <p className="text-slate-500 text-xs mt-1">Be specific — quantity, grade, material, size</p>

          {/* Example queries */}
          <div className="mt-3">
            <p className="text-xs text-slate-500 mb-2">Try an example:</p>
            <div className="flex flex-wrap gap-2">
              {EXAMPLE_QUERIES.map((q) => (
                <button
                  key={q}
                  onClick={() => setDescription(q)}
                  className="text-xs bg-slate-800 hover:bg-slate-700 text-slate-400 hover:text-white px-3 py-1.5 rounded-lg transition-colors border border-slate-700"
                >
                  {q.length > 40 ? q.slice(0, 40) + "…" : q}
                </button>
              ))}
            </div>
          </div>
        </div>

        {/* Supplier URLs */}
        <div className="mb-8">
          <label className="block text-sm font-semibold mb-2">
            Supplier websites <span className="text-slate-500 font-normal">(up to 3)</span>
          </label>

          {supplierUrls.map((url, i) => (
            <div key={i} className="mb-3">
              <div className="flex items-center gap-2 mb-1.5">
                <span className="text-xs text-slate-500 w-16">Supplier {i + 1}</span>
                <div className="flex gap-1.5">
                  {DEFAULT_SUPPLIERS.map((s) => (
                    <button
                      key={s.url}
                      onClick={() => usePreset(s.url, i)}
                      className={`text-xs px-2 py-1 rounded-md border transition-colors ${
                        url === s.url
                          ? "bg-green-400/10 border-green-400/30 text-green-400"
                          : "bg-slate-800 border-slate-700 text-slate-400 hover:text-white"
                      }`}
                    >
                      {s.name}
                    </button>
                  ))}
                </div>
              </div>
              <input
                type="url"
                value={url}
                onChange={(e) => updateUrl(i, e.target.value)}
                placeholder="https://supplier-website.com"
                className="w-full bg-brand-slate border border-slate-700 rounded-xl px-4 py-2.5 text-white placeholder-slate-500 focus:outline-none focus:border-green-500 text-sm"
              />
            </div>
          ))}
        </div>

        {/* Estimate banner */}
        <div className="flex items-center gap-3 bg-green-400/5 border border-green-400/20 rounded-xl p-4 mb-6">
          <Zap className="w-5 h-5 text-green-400 shrink-0" />
          <div>
            <p className="text-sm font-semibold text-green-400">⚡ Estimated completion: ~90 seconds</p>
            <p className="text-xs text-slate-400 mt-0.5">Human equivalent: 2 hrs 30 mins · You save ~97% of the time</p>
          </div>
        </div>

        {error && (
          <div className="bg-red-500/10 border border-red-500/30 text-red-400 text-sm rounded-xl p-3 mb-4">
            {error}
          </div>
        )}

        <button
          onClick={handleSubmit}
          disabled={loading}
          className="w-full flex items-center justify-center gap-2 bg-brand-green text-black font-bold py-4 rounded-xl hover:bg-green-400 transition-all disabled:opacity-50 disabled:cursor-not-allowed text-base"
        >
          {loading ? (
            <>
              <div className="w-4 h-4 border-2 border-black/30 border-t-black rounded-full animate-spin" />
              Launching agents...
            </>
          ) : (
            <>
              <Zap className="w-5 h-5" />
              Run Quote Hunt
            </>
          )}
        </button>
      </div>
    </AppShell>
  );
}
