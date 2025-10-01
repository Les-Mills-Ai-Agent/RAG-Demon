// src/components/FeedbackProvider.tsx
import React, { createContext, useCallback, useContext, useMemo, useState } from "react";
import { useAuth } from "react-oidc-context";
import { sendFeedback } from "../services/feedbackService";

export type Exchange = {
  question: string;
  answer: string;
  timestamp?: string;
};

export type FeedbackPayload = {
  issueType: string;
  severity: "Low" | "Medium" | "High";
  notes: string;
  includeContext: boolean;
};

type Ctx = {
  lastExchange: Exchange | null;
  setLastExchange: (e: Exchange | null) => void;
  open: () => void;
  close: () => void;
  isOpen: boolean;
  submit: (p: FeedbackPayload) => Promise<void>;
  submitting: boolean;
  error: string | null;
  ok: boolean;
};

const FeedbackContext = createContext<Ctx | null>(null);
export const useFeedback = () => {
  const ctx = useContext(FeedbackContext);
  if (!ctx) throw new Error("useFeedback must be used within <FeedbackProvider>");
  return ctx;
};

const ISSUE_TYPES = [
  "Incorrect answer",
  "Missing context",
  "Hallucination",
  "Not helpful",
  "Toxic / unsafe",
  "Latency / performance",
  "UI / UX issue",
  "Other",
];

export function FeedbackProvider({ children }: { children: React.ReactNode }) {
  const auth = useAuth();
  const [lastExchange, setLastExchange] = useState<Exchange | null>(null);
  const [isOpen, setIsOpen] = useState(false);
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [ok, setOk] = useState(false);

  const open  = useCallback(() => setIsOpen(true), []);
  const close = useCallback(() => setIsOpen(false), []);

  // lock page scroll when modal open
  React.useEffect(() => {
    if (isOpen) {
      const prev = document.body.style.overflow;
      document.body.style.overflow = "hidden";
      return () => { document.body.style.overflow = prev; };
    }
  }, [isOpen]);

  // tiny uuid for SK suffix
  const uuid = () =>
    // @ts-ignore
    ([1e7] as any +-1e3 +-4e3 +-8e3 +-1e11).replace(/[018]/g, (c: any) =>
      (c ^ crypto.getRandomValues(new Uint8Array(1))[0] & 15 >> c / 4).toString(16)
    );

  const submit = useCallback(async (payload: FeedbackPayload) => {
    setSubmitting(true); setError(null); setOk(false);
    const submittedAt = new Date().toISOString();
    const sessionId = (window as any).__LES_MILLS_SESSION__ || uuid();

    const item = {
      pk: "APP#lesmills",
      sk: `FEEDBACK#${submittedAt}#${uuid()}`,
      sessionId,
      issueType: payload.issueType,
      severity: payload.severity,
      notes: payload.notes || "",
      includeContext: payload.includeContext,
      question: payload.includeContext ? lastExchange?.question ?? null : null,
      answer:   payload.includeContext ? lastExchange?.answer   ?? null : null,
      submittedAt,
      metadata: {
        userAgent: navigator.userAgent,
        language: navigator.language,
        tzOffsetMin: new Date().getTimezoneOffset(),
      },
    };

    try {
      await sendFeedback(item, auth.user?.id_token);
      setOk(true);
      setIsOpen(false);
    } catch (e: any) {
      setError(e?.message || "Failed to submit feedback");
    } finally {
      setSubmitting(false);
    }
  }, [lastExchange, auth.user?.id_token]);

  const value = useMemo(() => ({
    lastExchange, setLastExchange, open, close, isOpen, submit, submitting, error, ok
  }), [lastExchange, open, close, isOpen, submit, submitting, error, ok]);

  return (
    <FeedbackContext.Provider value={value}>
      {children}
      <FeedbackModal />
    </FeedbackContext.Provider>
  );
}

function FeedbackModal() {
  const { isOpen, close, submit, lastExchange, submitting, error, ok } = useFeedback();
  const [issueType, setIssueType] = useState(ISSUE_TYPES[0]);
  const [severity, setSeverity]   = useState<"Low" | "Medium" | "High">("Low");
  const [notes, setNotes]         = useState("");
  const [includeContext, setIncludeContext] = useState(true);

  React.useEffect(() => {
    if (!isOpen) {
      setIssueType(ISSUE_TYPES[0]);
      setSeverity("Low");
      setNotes("");
      setIncludeContext(true);
    }
  }, [isOpen]);

  // close on Escape
  React.useEffect(() => {
    const onKey = (e: KeyboardEvent) => { if (e.key === "Escape" && isOpen) close(); };
    window.addEventListener("keydown", onKey);
    return () => window.removeEventListener("keydown", onKey);
  }, [isOpen, close]);

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center">
      {/* Backdrop */}
      <div className="absolute inset-0 bg-black/30" onClick={close} />

      {/* Panel: fixed width, scrollable content */}
      <div className="relative w-full sm:max-w-2xl max-h-[85vh] overflow-y-auto bg-white dark:bg-gray-800 rounded-2xl shadow-xl border border-gray-200 dark:border-gray-700 m-4">
        {/* Sticky header for nice UX while scrolling */}
        <div className="sticky top-0 z-10 bg-white/90 dark:bg-gray-800/90 backdrop-blur px-4 sm:px-6 py-4 border-b border-gray-200 dark:border-gray-700 flex items-start justify-between gap-4">
          <div>
            <h2 className="text-lg font-semibold">Give feedback on the last answer</h2>
            <p className="text-sm text-gray-500 dark:text-gray-400">This helps us improve responses.</p>
          </div>
          <button onClick={close} className="p-2 rounded-full hover:bg-gray-100 dark:hover:bg-gray-700" aria-label="Close">✕</button>
        </div>

        {/* Scrollable body */}
        <div className="px-4 sm:px-6 py-4 space-y-4">
          {/* Context preview */}
          <div className="grid gap-2 text-sm">
            <div className="p-3 rounded-xl bg-gray-50 dark:bg-gray-700/60 border border-gray-200 dark:border-gray-700">
              <div className="text-xs uppercase tracking-wide text-gray-500 dark:text-gray-300 mb-1">User said</div>
              <p className="whitespace-pre-wrap">{lastExchange?.question || "—"}</p>
            </div>
            <div className="p-3 rounded-xl bg-gray-50 dark:bg-gray-700/60 border border-gray-200 dark:border-gray-700">
              <div className="text-xs uppercase tracking-wide text-gray-500 dark:text-gray-300 mb-1">AI answered</div>
              <p className="whitespace-pre-wrap">{lastExchange?.answer || "—"}</p>
            </div>
          </div>

          {/* Form */}
          <form
            className="grid gap-4"
            onSubmit={(e) => { e.preventDefault(); submit({ issueType, severity, notes, includeContext }); }}
          >
            <label className="grid gap-1 text-sm">
              <span className="text-gray-700 dark:text-gray-200 font-medium">Issue type</span>
              <select
                value={issueType}
                onChange={(e) => setIssueType(e.target.value)}
                className="w-full rounded-xl border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-800 px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500"
                required
              >
                {ISSUE_TYPES.map(t => <option key={t} value={t}>{t}</option>)}
              </select>
            </label>

            <div className="flex items-center gap-2">
              {(["Low", "Medium", "High"] as const).map(s => (
                <label key={s} className={`flex-1 inline-flex items-center justify-center rounded-xl border px-3 py-2 text-sm cursor-pointer transition ${
                  severity === s ? "border-indigo-500 ring-1 ring-indigo-200 bg-indigo-50 dark:bg-indigo-900/30" : "border-gray-300 dark:border-gray-600 hover:bg-gray-50 dark:hover:bg-gray-700"
                }`}>
                  <input type="radio" className="hidden" checked={severity === s} onChange={() => setSeverity(s)} />
                  {s}
                </label>
              ))}
            </div>

            <label className="grid gap-1 text-sm">
              <span className="text-gray-700 dark:text-gray-200 font-medium">Notes</span>
              <textarea
                value={notes}
                onChange={(e) => setNotes(e.target.value)}
                placeholder="What went wrong (or right)?"
                className="w-full min-h-[100px] rounded-xl border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-800 px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500"
              />
            </label>

            <label className="inline-flex items-center gap-2 text-sm">
              <input
                type="checkbox"
                checked={includeContext}
                onChange={(e) => setIncludeContext(e.target.checked)}
                className="rounded border-gray-300 dark:border-gray-600"
              />
              Include the last question &amp; answer in my report
            </label>

            <div className="flex items-center justify-between pt-2 text-sm">
              <div>
                {submitting && <span className="text-gray-500">Submitting…</span>}
                {!submitting && error && <span className="text-red-600">{error}</span>}
                {!submitting && ok && <span className="text-green-600">Thanks! Feedback sent.</span>}
              </div>
              <div className="flex items-center gap-3">
                <button type="button" onClick={close} className="rounded-xl border border-gray-300 dark:border-gray-600 px-4 py-2 hover:bg-gray-50 dark:hover:bg-gray-700">Cancel</button>
                <button type="submit" disabled={submitting} className="rounded-xl bg-indigo-600 text-white px-4 py-2 hover:bg-indigo-700 disabled:opacity-60">Submit feedback</button>
              </div>
            </div>
          </form>
        </div>
        {/* end body */}
      </div>
    </div>
  );
}
