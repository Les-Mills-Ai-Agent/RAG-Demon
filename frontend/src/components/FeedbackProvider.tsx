import React, { createContext, useCallback, useContext, useEffect, useMemo, useState } from "react";
import { useAuth } from "react-oidc-context";
import { v4 as uuidv4 } from "uuid";
import { sendFeedback } from "../services/feedbackService";

/** Last user/AI exchange we’re attaching feedback to */
export type Exchange = { question: string; answer: string; timestamp?: string; };

/** Payload from the feedback form */
export type FeedbackPayload = { issueType: string; severity: "Low" | "Medium" | "High"; notes: string; includeContext: boolean; };

/** Public shape exposed via context */
type FeedbackContextValue = {
  lastExchange: Exchange | null; setLastExchange: (e: Exchange | null) => void;
  open: () => void; close: () => void; isOpen: boolean;
  submit: (p: FeedbackPayload) => Promise<void>;
  submitting: boolean; error: string | null; ok: boolean;
};

/** Select options for “Issue type” (UI reads from here) */
const ISSUE_TYPES = [
  "Incorrect answer","Missing context","Hallucination","Not helpful",
  "Toxic / unsafe","Latency / performance","UI / UX issue","Other",
] as const;

/** Internal context used by ChatBubble + Modal */
const FeedbackContext = createContext<FeedbackContextValue | null>(null);

/** Hook for consumers (throws if not wrapped by provider) */
export const useFeedback = (): FeedbackContextValue => {
  const ctx = useContext(FeedbackContext);
  if (!ctx) throw new Error("useFeedback must be used within <FeedbackProvider>");
  return ctx;
};

/** Session id for grouping feedback (fallback to uuid if not set) */
const getSessionId = () => (window as any).__LES_MILLS_SESSION__ || uuidv4();

/** Build the DynamoDB item we POST to backend (kept here for testability) */
const buildFeedbackItem = (
  payload: FeedbackPayload,
  lastExchange: Exchange | null,
  sessionId: string,
  authUser?: any
) => {
  const submittedAt = new Date().toISOString();

  return {
    sessionId,
    issueType: payload.issueType,
    severity: payload.severity,
    notes: payload.notes || "",
    includeContext: true, // always include context
    question: lastExchange?.question ?? null,
    answer: lastExchange?.answer ?? null,
    submittedAt,
    metadata: { 
      userAgent: navigator.userAgent, 
      language: navigator.language, 
      tzOffsetMin: new Date().getTimezoneOffset() 
    },
  };
};

/** Provider: exposes modal controls + submit while rendering the modal */
export function FeedbackProvider({ children }: { children: React.ReactNode }) {
  const auth = useAuth();
  const [lastExchange, setLastExchange] = useState<Exchange | null>(null);
  const [isOpen, setIsOpen] = useState(false);
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [ok, setOk] = useState(false);

  const open = useCallback(() => setIsOpen(true), []);
  const close = useCallback(() => setIsOpen(false), []);

  // Prevent background scroll while modal is open
  useEffect(() => {
    if (!isOpen) return;
    const prev = document.body.style.overflow;
    document.body.style.overflow = "hidden";
    return () => { document.body.style.overflow = prev; };
  }, [isOpen]);

  // Submit feedback to backend (includes auth token; required)
  const submit = useCallback(async (payload: FeedbackPayload) => {
    setSubmitting(true);
    setError(null);
    setOk(false);

    const item = buildFeedbackItem(payload, lastExchange, getSessionId());

    // Guard: id_token must exist
    const token = auth.user?.id_token;
    if (!token) {
      setSubmitting(false);
      setError("Missing auth token. Please sign in again.");
      return;
    }

    try {
      // Add Bearer prefix so Cognito authoriser recognises token
      await sendFeedback(item, `Bearer ${token}`);
      setOk(true);
      setIsOpen(false);
    } catch (e: unknown) {
      setError(e instanceof Error ? e.message : "Failed to submit feedback");
    } finally {
      setSubmitting(false);
    }
  }, [lastExchange, auth.user]);

  // Stable value for consumers
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

/** Modal UI: reads/writes state via context; UI classes unchanged */
function FeedbackModal() {
  const { isOpen, close, submit, lastExchange, submitting, error, ok } = useFeedback();
  const [issueType, setIssueType] = useState<string>(ISSUE_TYPES[0]);
  const [severity, setSeverity] = useState<"Low" | "Medium" | "High">("Low");
  const [notes, setNotes] = useState<string>("");
  const [includeContext, setIncludeContext] = useState<boolean>(true);

  // Reset form each time modal closes
  useEffect(() => { if (!isOpen) { setIssueType(ISSUE_TYPES[0]); setSeverity("Low"); setNotes(""); setIncludeContext(true); } }, [isOpen]);

  // Close on ESC for accessibility
  useEffect(() => {
    const onKey = (e: KeyboardEvent) => { if (e.key === "Escape" && isOpen) close(); };
    window.addEventListener("keydown", onKey);
    return () => window.removeEventListener("keydown", onKey);
  }, [isOpen, close]);

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center">
      {/* Backdrop (click to close) */}
      <div className="absolute inset-0 bg-black/30" onClick={close} />
      {/* Scrollable panel (size unchanged) */}
      <div className="relative w-full sm:max-w-2xl max-h-[85vh] overflow-y-auto bg-white dark:bg-gray-800 rounded-2xl shadow-xl border border-gray-200 dark:border-gray-700 m-4">
        {/* Sticky header */}
        <div className="sticky top-0 z-10 bg-white/90 dark:bg-gray-800/90 backdrop-blur px-4 sm:px-6 py-4 border-b border-gray-200 dark:border-gray-700 flex items-start justify-between gap-4">
          <div>
            <h2 className="text-lg font-semibold">Give feedback on the last answer</h2>
            <p className="text-sm text-gray-500 dark:text-gray-400">This helps us improve responses.</p>
          </div>
          <button onClick={close} className="p-2 rounded-full hover:bg-gray-100 dark:hover:bg-gray-700" aria-label="Close">✕</button>
        </div>

        {/* Body */}
        <div className="px-4 sm:px-6 py-4 space-y-4">
          {/* Context preview cards */}
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
          <form className="grid gap-4" onSubmit={(e) => { e.preventDefault(); submit({ issueType, severity, notes, includeContext }); }}>
            <label className="grid gap-1 text-sm">
              <span className="text-gray-700 dark:text-gray-200 font-medium">Issue type</span>
              <select value={issueType} onChange={(e) => setIssueType(e.target.value)} className="w-full rounded-xl border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-800 px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500" required>
                {ISSUE_TYPES.map((t) => <option key={t} value={t}>{t}</option>)}
              </select>
            </label>

            {/* Severity toggle (three-pill radio group) */}
            <div className="flex items-center gap-2">
              {(["Low","Medium","High"] as const).map((s) => (
                <label key={s} className={`flex-1 inline-flex items-center justify-center rounded-xl border px-3 py-2 text-sm cursor-pointer transition ${severity===s ? "border-indigo-500 ring-1 ring-indigo-200 bg-indigo-50 dark:bg-indigo-900/30" : "border-gray-300 dark:border-gray-600 hover:bg-gray-50 dark:hover:bg-gray-700"}`}>
                  <input type="radio" className="hidden" checked={severity===s} onChange={() => setSeverity(s)} />
                  {s}
                </label>
              ))}
            </div>

            <label className="grid gap-1 text-sm">
              <span className="text-gray-700 dark:text-gray-200 font-medium">Notes</span>
              <textarea value={notes} onChange={(e) => setNotes(e.target.value)} placeholder="What went wrong (or right)?" className="w-full min-h-[100px] rounded-xl border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-800 px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500" />
            </label>

            {/* Footer: status + actions */}
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
      </div>
    </div>
  );
}
