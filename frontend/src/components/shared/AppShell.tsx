// src/components/shared/AppShell.tsx
"use client";
import Link from "next/link";
import { usePathname } from "next/navigation";
import { Search, LayoutDashboard, Building2, Plus } from "lucide-react";
import { useEffect, useState } from "react";
import { getActiveAgents } from "@/lib/api";

export default function AppShell({ children }: { children: React.ReactNode }) {
  const path = usePathname();
  const [activeAgents, setActiveAgents] = useState(0);

  useEffect(() => {
    const fetch = () => getActiveAgents().then(setActiveAgents).catch(() => {});
    fetch();
    const t = setInterval(fetch, 10000);
    return () => clearInterval(t);
  }, []);

  const navItems = [
    { href: "/dashboard", label: "Dashboard", icon: LayoutDashboard },
    { href: "/quotes/new", label: "New Hunt", icon: Plus },
    { href: "/suppliers", label: "Suppliers", icon: Building2 },
  ];

  return (
    <div className="min-h-screen flex flex-col">
      {/* Top nav */}
      <nav className="border-b border-slate-800 px-6 py-3 flex items-center gap-6">
        <Link href="/" className="flex items-center gap-2 shrink-0">
          <div className="w-7 h-7 bg-brand-green rounded-lg flex items-center justify-center">
            <Search className="w-3.5 h-3.5 text-black" />
          </div>
          <span className="font-bold tracking-tight">ProcureIQ</span>
        </Link>

        <div className="flex items-center gap-1 flex-1">
          {navItems.map((item) => (
            <Link
              key={item.href}
              href={item.href}
              className={`flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-sm transition-colors ${
                path === item.href
                  ? "bg-slate-800 text-white"
                  : "text-slate-400 hover:text-white hover:bg-slate-800/50"
              }`}
            >
              <item.icon className="w-3.5 h-3.5" />
              {item.label}
            </Link>
          ))}
        </div>

        {activeAgents > 0 && (
          <span className="flex items-center gap-1.5 text-xs text-slate-400">
            <span className="w-1.5 h-1.5 bg-green-400 rounded-full animate-pulse" />
            {activeAgents} agent{activeAgents !== 1 ? "s" : ""} active
          </span>
        )}
      </nav>

      <main className="flex-1">{children}</main>
    </div>
  );
}
