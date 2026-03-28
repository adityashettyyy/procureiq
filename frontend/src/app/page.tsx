"use client";
import Link from "next/link";
import { Zap, Search, BarChart3, ArrowRight, CheckCircle, Globe } from "lucide-react";
import { useEffect, useState } from "react";
import { getMetrics, getActiveAgents, type Metrics } from "@/lib/api";

export default function LandingPage() {
  const [metrics, setMetrics] = useState<Metrics | null>(null);
  const [activeAgents, setActiveAgents] = useState(0);

  useEffect(() => {
    getMetrics().then(setMetrics).catch(() => {});
    getActiveAgents().then(setActiveAgents).catch(() => {});
  }, []);

  return (
    <main className="min-h-screen flex flex-col">
      {/* Nav */}
      <nav className="border-b border-slate-800 px-6 py-4 flex items-center justify-between">
        <div className="flex items-center gap-2">
          <div className="w-8 h-8 bg-brand-green rounded-lg flex items-center justify-center">
            <Search className="w-4 h-4 text-black" />
          </div>
          <span className="font-bold text-xl tracking-tight">ProcureIQ</span>
        </div>
        <div className="flex items-center gap-4">
          {activeAgents > 0 && (
            <span className="flex items-center gap-1.5 text-sm text-slate-400">
              <span className="w-2 h-2 bg-green-400 rounded-full animate-pulse" />
              {activeAgents} agent{activeAgents !== 1 ? "s" : ""} active
            </span>
          )}
          <Link href="/dashboard" className="text-sm text-slate-400 hover:text-white transition-colors">
            Dashboard
          </Link>
          <Link
            href="/quotes/new"
            className="bg-brand-green text-black text-sm font-semibold px-4 py-2 rounded-lg hover:bg-green-400 transition-colors"
          >
            Try Free
          </Link>
        </div>
      </nav>

      {/* Hero */}
      <section className="flex-1 flex flex-col items-center justify-center px-6 py-24 text-center">
        <div className="inline-flex items-center gap-2 bg-green-400/10 border border-green-400/20 rounded-full px-4 py-1.5 mb-8">
          <Zap className="w-3.5 h-3.5 text-green-400" />
          <span className="text-green-400 text-sm font-medium">Powered by TinyFish Web Agents</span>
        </div>

        <h1 className="text-5xl md:text-7xl font-black tracking-tight mb-6 max-w-4xl leading-tight">
          3 supplier quotes.{" "}
          <span className="text-brand-green">90 seconds.</span>{" "}
          Zero manual work.
        </h1>

        <p className="text-xl text-slate-400 max-w-2xl mb-10 leading-relaxed">
          ProcureIQ deploys autonomous web agents that navigate real supplier websites,
          extract live pricing, and deliver a ranked comparison — while your team
          does literally anything else.
        </p>

        <div className="flex flex-col sm:flex-row gap-4">
          <Link
            href="/quotes/new"
            className="flex items-center gap-2 bg-brand-green text-black font-bold px-8 py-4 rounded-xl hover:bg-green-400 transition-all hover:scale-105 text-lg"
          >
            Run Your First Quote Hunt
            <ArrowRight className="w-5 h-5" />
          </Link>
          <Link
            href="/dashboard"
            className="flex items-center gap-2 border border-slate-700 text-slate-300 font-semibold px-8 py-4 rounded-xl hover:border-slate-500 transition-colors text-lg"
          >
            View Dashboard
          </Link>
        </div>

        {/* Live metrics bar */}
        {metrics && (
          <div className="mt-16 flex flex-wrap justify-center gap-8 text-center">
            {[
              { label: "Quote hunts run", value: metrics.total_jobs },
              { label: "Supplier quotes collected", value: metrics.total_quotes_collected },
              { label: "Hours saved", value: `${metrics.total_hours_saved}h` },
            ].map((stat) => (
              <div key={stat.label}>
                <div className="text-3xl font-black text-white">{stat.value}</div>
                <div className="text-sm text-slate-500 mt-1">{stat.label}</div>
              </div>
            ))}
          </div>
        )}
      </section>

      {/* How it works */}
      <section className="border-t border-slate-800 px-6 py-20">
        <div className="max-w-5xl mx-auto">
          <h2 className="text-3xl font-bold text-center mb-12">How it works</h2>
          <div className="grid md:grid-cols-3 gap-8">
            {[
              { icon: Search, step: "01", title: "Describe what you need", desc: "Type your product requirement in plain English. Quantity, spec, grade — we parse it all." },
              { icon: Globe, step: "02", title: "Agents hit the web", desc: "3 autonomous TinyFish agents simultaneously navigate real supplier websites. No databases. Live data." },
              { icon: BarChart3, step: "03", title: "Compare & decide", desc: "Get a ranked comparison with pricing, lead times, and availability. Export CSV or generate an RFQ email in one click." },
            ].map((item) => (
              <div key={item.step} className="bg-brand-slate rounded-2xl p-6 border border-slate-700">
                <div className="flex items-center gap-3 mb-4">
                  <div className="w-10 h-10 bg-green-400/10 rounded-lg flex items-center justify-center">
                    <item.icon className="w-5 h-5 text-green-400" />
                  </div>
                  <span className="text-slate-600 font-mono text-sm">{item.step}</span>
                </div>
                <h3 className="font-bold text-lg mb-2">{item.title}</h3>
                <p className="text-slate-400 text-sm leading-relaxed">{item.desc}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Why TinyFish */}
      <section className="border-t border-slate-800 px-6 py-16 bg-brand-slate/50">
        <div className="max-w-3xl mx-auto text-center">
          <h2 className="text-2xl font-bold mb-4">Impossible without a real browser agent</h2>
          <p className="text-slate-400 mb-8">
            This product doesn't exist without TinyFish. No database holds live supplier prices.
            No API gives you real-time MOQ and stock availability. We navigate real websites —
            search bars, pricing tables, pop-ups, pagination — just like a human would.
            Just 150× faster.
          </p>
          <div className="flex flex-wrap justify-center gap-3">
            {["Multi-step navigation", "Dynamic UI handling", "Session management", "Form interaction", "Pagination", "Pop-up dismissal"].map((f) => (
              <span key={f} className="flex items-center gap-1.5 bg-slate-800 text-slate-300 text-sm px-3 py-1.5 rounded-full border border-slate-700">
                <CheckCircle className="w-3.5 h-3.5 text-green-400" />
                {f}
              </span>
            ))}
          </div>
        </div>
      </section>

      {/* Footer */}
      <footer className="border-t border-slate-800 px-6 py-8 flex flex-col sm:flex-row items-center justify-between gap-4">
        <div className="flex items-center gap-2 text-slate-500 text-sm">
          <Search className="w-4 h-4" />
          <span>ProcureIQ — Built at TinyFish Pre-Accelerator Hackathon 2025</span>
        </div>
        <div className="flex items-center gap-4 text-sm text-slate-500">
          <a href="https://github.com/yourteam/procureiq" target="_blank" className="hover:text-white transition-colors">
            GitHub
          </a>
          <span className="flex items-center gap-1">
            Powered by <span className="text-green-400 font-semibold ml-1">TinyFish</span>
          </span>
        </div>
      </footer>
    </main>
  );
}
