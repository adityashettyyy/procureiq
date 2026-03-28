"use client";
import { Brain } from "lucide-react";
import type { ParsedQuery } from "@/lib/api";

export default function ParsedQueryBanner({ query }: { query: ParsedQuery }) {
  const fields = [
    { label: "Product",   value: query.product },
    { label: "Grade",     value: query.grade },
    { label: "Quantity",  value: query.quantity?.toString() },
    { label: "Material",  value: query.material },
  ].filter((f) => f.value);

  return (
    <div className="bg-blue-400/5 border border-blue-400/20 rounded-xl p-4 mb-6">
      <div className="flex items-start gap-3">
        <Brain className="w-4 h-4 text-blue-400 mt-0.5 shrink-0" />
        <div className="flex-1 min-w-0">
          <p className="text-xs font-semibold text-blue-400 mb-2">🧠 Query understood as:</p>
          <div className="flex flex-wrap gap-x-6 gap-y-1 mb-2">
            {fields.map((f) => (
              <span key={f.label} className="text-xs text-slate-300">
                <span className="text-slate-500">{f.label}:</span>{" "}
                <span className="font-semibold">{f.value}</span>
              </span>
            ))}
          </div>
          {query.search_string && (
            <p className="text-xs text-slate-400">
              Searching with:{" "}
              <span className="font-mono bg-slate-800 px-2 py-0.5 rounded text-blue-300">
                "{query.search_string}"
              </span>
            </p>
          )}
        </div>
      </div>
    </div>
  );
}
