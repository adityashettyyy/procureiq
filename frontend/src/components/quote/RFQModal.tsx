"use client";
import { useState } from "react";
import { X, Copy, Check, Mail } from "lucide-react";
import type { QuoteResult, RFQDraft } from "@/lib/api";

interface Props {
  result: QuoteResult;
  draft: RFQDraft | null;
  loading: boolean;
  onClose: () => void;
}

export default function RFQModal({ result, draft, loading, onClose }: Props) {
  const [copied, setCopied] = useState(false);

  const copy = async (text: string) => {
    await navigator.clipboard.writeText(text);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  const fullEmail = draft ? `Subject: ${draft.subject}\n\n${draft.body}` : "";

  return (
    <div className="fixed inset-0 bg-black/70 backdrop-blur-sm z-50 flex items-center justify-center p-4">
      <div className="bg-brand-slate border border-slate-700 rounded-2xl w-full max-w-2xl max-h-[90vh] flex flex-col">
        {/* Header */}
        <div className="flex items-center justify-between px-6 py-4 border-b border-slate-700">
          <div className="flex items-center gap-2">
            <Mail className="w-5 h-5 text-green-400" />
            <h2 className="font-bold">RFQ Email Draft</h2>
          </div>
          <button onClick={onClose} className="text-slate-400 hover:text-white transition-colors">
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Content */}
        <div className="flex-1 overflow-y-auto p-6">
          {loading ? (
            <div className="flex flex-col items-center justify-center py-12 gap-3">
              <div className="w-6 h-6 border-2 border-green-400/30 border-t-green-400 rounded-full animate-spin" />
              <p className="text-slate-400 text-sm">Generating RFQ email...</p>
            </div>
          ) : draft ? (
            <div className="space-y-4">
              {/* Subject */}
              <div>
                <label className="block text-xs text-slate-500 mb-1 uppercase tracking-wide">Subject</label>
                <div className="bg-slate-800 border border-slate-700 rounded-lg px-4 py-2.5 text-sm font-medium">
                  {draft.subject}
                </div>
              </div>

              {/* Body */}
              <div>
                <label className="block text-xs text-slate-500 mb-1 uppercase tracking-wide">Body</label>
                <textarea
                  readOnly
                  value={draft.body}
                  rows={12}
                  className="w-full bg-slate-800 border border-slate-700 rounded-lg px-4 py-3 text-sm text-slate-200 resize-none focus:outline-none focus:border-green-500/50 font-mono leading-relaxed"
                />
              </div>

              {/* Recipient hint */}
              {draft.recipient_hint && (
                <p className="text-xs text-slate-500">
                  💡 <strong>Send to:</strong> {draft.recipient_hint}
                </p>
              )}
            </div>
          ) : (
            <p className="text-slate-400 text-center py-8">Failed to generate email. Please try again.</p>
          )}
        </div>

        {/* Actions */}
        {draft && (
          <div className="flex items-center gap-3 px-6 py-4 border-t border-slate-700">
            <button
              onClick={() => copy(fullEmail)}
              className="flex items-center gap-2 bg-green-500 text-black font-semibold px-5 py-2.5 rounded-lg hover:bg-green-400 transition-colors text-sm"
            >
              {copied ? <Check className="w-4 h-4" /> : <Copy className="w-4 h-4" />}
              {copied ? "Copied!" : "Copy to Clipboard"}
            </button>
            <a
              href={`mailto:?subject=${encodeURIComponent(draft.subject)}&body=${encodeURIComponent(draft.body)}`}
              className="flex items-center gap-2 border border-slate-700 text-slate-300 hover:text-white px-5 py-2.5 rounded-lg transition-colors text-sm"
            >
              <Mail className="w-4 h-4" />
              Open in Mail
            </a>
            <button onClick={onClose} className="ml-auto text-slate-400 hover:text-white text-sm transition-colors">
              Close
            </button>
          </div>
        )}
      </div>
    </div>
  );
}
