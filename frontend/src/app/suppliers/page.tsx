"use client";
import { useEffect, useState } from "react";
import { Plus, Trash2, CheckCircle, Building2 } from "lucide-react";
import { listSuppliers, createSupplier, deleteSupplier, type Supplier } from "@/lib/api";
import AppShell from "@/components/shared/AppShell";

const CATEGORIES = ["Industrial & B2B", "General Procurement", "Global Manufacturing", "Export & Manufacturing", "Electronics", "Other"];

export default function SuppliersPage() {
  const [suppliers, setSuppliers] = useState<Supplier[]>([]);
  const [loading, setLoading] = useState(true);
  const [showForm, setShowForm] = useState(false);
  const [form, setForm] = useState({ name: "", url: "", category: "Industrial & B2B" });
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState("");

  const load = () =>
    listSuppliers()
      .then(setSuppliers)
      .catch(console.error)
      .finally(() => setLoading(false));

  useEffect(() => { load(); }, []);

  const handleAdd = async () => {
    if (!form.name.trim() || !form.url.trim()) { setError("Name and URL are required."); return; }
    setSaving(true); setError("");
    try {
      await createSupplier(form);
      setForm({ name: "", url: "", category: "Industrial & B2B" });
      setShowForm(false);
      load();
    } catch { setError("Failed to add supplier."); }
    finally { setSaving(false); }
  };

  const handleDelete = async (id: string) => {
    if (!confirm("Remove this supplier?")) return;
    await deleteSupplier(id);
    load();
  };

  return (
    <AppShell>
      <div className="max-w-4xl mx-auto px-6 py-8">
        {/* Header */}
        <div className="flex items-center justify-between mb-8">
          <div>
            <h1 className="text-2xl font-bold">Supplier Library</h1>
            <p className="text-slate-400 text-sm mt-1">Manage your pre-configured supplier websites</p>
          </div>
          <button
            onClick={() => setShowForm(!showForm)}
            className="flex items-center gap-2 bg-brand-green text-black font-bold px-4 py-2.5 rounded-xl hover:bg-green-400 transition-colors text-sm"
          >
            <Plus className="w-4 h-4" />
            Add Supplier
          </button>
        </div>

        {/* Add form */}
        {showForm && (
          <div className="bg-brand-slate border border-slate-700 rounded-xl p-5 mb-6 animate-fade-in">
            <h3 className="font-semibold mb-4">Add New Supplier</h3>
            <div className="grid md:grid-cols-3 gap-3 mb-3">
              <input
                placeholder="Supplier name"
                value={form.name}
                onChange={(e) => setForm({ ...form, name: e.target.value })}
                className="bg-slate-800 border border-slate-700 rounded-lg px-3 py-2.5 text-sm text-white placeholder-slate-500 focus:outline-none focus:border-green-500"
              />
              <input
                placeholder="https://supplier.com"
                value={form.url}
                onChange={(e) => setForm({ ...form, url: e.target.value })}
                className="bg-slate-800 border border-slate-700 rounded-lg px-3 py-2.5 text-sm text-white placeholder-slate-500 focus:outline-none focus:border-green-500"
              />
              <select
                value={form.category}
                onChange={(e) => setForm({ ...form, category: e.target.value })}
                className="bg-slate-800 border border-slate-700 rounded-lg px-3 py-2.5 text-sm text-white focus:outline-none focus:border-green-500"
              >
                {CATEGORIES.map((c) => <option key={c}>{c}</option>)}
              </select>
            </div>
            {error && <p className="text-red-400 text-xs mb-3">{error}</p>}
            <div className="flex gap-2">
              <button
                onClick={handleAdd}
                disabled={saving}
                className="bg-green-500 text-black font-semibold px-4 py-2 rounded-lg text-sm hover:bg-green-400 transition-colors disabled:opacity-50"
              >
                {saving ? "Saving..." : "Save Supplier"}
              </button>
              <button
                onClick={() => { setShowForm(false); setError(""); }}
                className="text-slate-400 hover:text-white text-sm px-4 py-2"
              >
                Cancel
              </button>
            </div>
          </div>
        )}

        {/* Suppliers grid */}
        {loading ? (
          <div className="text-center text-slate-500 py-12">Loading suppliers...</div>
        ) : (
          <div className="grid md:grid-cols-2 gap-4">
            {suppliers.map((s) => (
              <div key={s.id} className="bg-brand-slate border border-slate-700 rounded-xl p-5 flex items-start justify-between gap-3">
                <div className="flex items-start gap-3 flex-1 min-w-0">
                  <div className="w-10 h-10 bg-slate-800 rounded-lg flex items-center justify-center shrink-0">
                    <Building2 className="w-5 h-5 text-slate-500" />
                  </div>
                  <div className="min-w-0">
                    <div className="flex items-center gap-2">
                      <h3 className="font-semibold text-white">{s.name}</h3>
                      {s.is_verified && (
                        <CheckCircle className="w-3.5 h-3.5 text-green-400 shrink-0" />
                      )}
                    </div>
                    <a
                      href={s.url}
                      target="_blank"
                      className="text-xs text-slate-500 hover:text-blue-400 transition-colors truncate block"
                    >
                      {s.url}
                    </a>
                    <div className="flex items-center gap-3 mt-2 flex-wrap">
                      {s.category && (
                        <span className="text-xs bg-slate-800 text-slate-400 px-2 py-0.5 rounded">
                          {s.category}
                        </span>
                      )}
                      {s.trust_score && (
                        <span className="text-xs text-green-400 font-semibold">
                          ⭐ {s.trust_score}/100
                        </span>
                      )}
                      {s.avg_response_time && (
                        <span className="text-xs text-slate-500">
                          Avg response: {s.avg_response_time}
                        </span>
                      )}
                    </div>
                  </div>
                </div>
                <button
                  onClick={() => handleDelete(s.id)}
                  className="text-slate-600 hover:text-red-400 transition-colors shrink-0"
                >
                  <Trash2 className="w-4 h-4" />
                </button>
              </div>
            ))}
          </div>
        )}
      </div>
    </AppShell>
  );
}
