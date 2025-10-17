import React, { useState, useRef, useEffect } from "react";
import ReactMarkdown from "react-markdown";
import dayjs from "dayjs";
import { Message, ErrorResponse } from "../models/models";
import { useFeedback } from "./FeedbackProvider";

interface ChatBubbleProps {
  msg: Message;
  isLoading: boolean;
  error: ErrorResponse | null;
  onRetry?: () => void;
  lastUserText?: string;
}

const ChatBubble: React.FC<ChatBubbleProps> = ({
  msg,
  isLoading,
  error,
  onRetry,
  lastUserText,
}) => {
  const base =
    "relative inline-block max-w-[40rem] px-4 py-3 rounded-2xl text-[13px] leading-relaxed text-left shadow-sm animate-fadeIn";
  const classes =
    msg.role === "user"
      ? `${base} bg-blue-100 text-gray-800 self-end dark:bg-blue-300 dark:text-black`
      : `${base} ${
          error
            ? "bg-red-100 text-red-700 dark:bg-red-400"
            : "bg-gray-100 text-gray-800 dark:bg-gray-700 dark:text-gray-100"
        } self-start`;

  const formattedTime = msg.created_at
    ? dayjs(msg.created_at).format("h:mm A")
    : null;

  // 3-dot menu state & refs (AI bubbles only)
  const [menuOpen, setMenuOpen] = useState(false);
  const menuRef = useRef<HTMLDivElement | null>(null);

  // feedback context
  const { setLastExchange, open } = useFeedback();

  // close menu on outside click
  useEffect(() => {
    if (!menuOpen) return;
    const onClick = (e: MouseEvent) => {
      if (menuRef.current && !menuRef.current.contains(e.target as Node)) {
        setMenuOpen(false);
      }
    };
    window.addEventListener("mousedown", onClick);
    return () => window.removeEventListener("mousedown", onClick);
  }, [menuOpen]);

  // close on ESC & lock scroll
  useEffect(() => {
    if (!menuOpen) return;
    const onKey = (e: KeyboardEvent) =>
      e.key === "Escape" && setMenuOpen(false);
    const prev = document.body.style.overflow;
    document.body.style.overflow = "hidden";
    window.addEventListener("keydown", onKey);
    return () => {
      document.body.style.overflow = prev;
      window.removeEventListener("keydown", onKey);
    };
  }, [menuOpen]);

  const handleGiveFeedback = () => {
    setLastExchange({
      question: lastUserText ?? "",
      answer: msg.content ?? "",
      timestamp: new Date().toISOString(),
    });
    open();
    setMenuOpen(false);
  };

  const handleCopy = async () => {
    try {
      await navigator.clipboard.writeText(msg.content || "");
    } catch {}
    setMenuOpen(false);
  };

  return (
    <div
      className={`w-full flex ${
        msg.role === "user" ? "justify-end" : "justify-start"
      }`}
    >
      <div
        className={`flex items-end gap-2 ${
          msg.role === "user" ? "flex-row-reverse" : ""
        }`}
      >
        {msg.role === "ai" && (
          <div className="bg-red-500 text-white rounded-full w-8 h-8 flex items-center justify-center text-sm font-bold shrink-0">
            LMI
          </div>
        )}

        <div className={classes}>
          {/* Loading */}
          {isLoading && (
            <div className="flex gap-1 text-gray-500">
              <span className="animate-blink delay-0">.</span>
              <span className="animate-blink delay-200">.</span>
              <span className="animate-blink delay-400">.</span>
            </div>
          )}

          {/* Error */}
          {error && (
            <>
              <div>⚠️ {error.message || "Something went wrong."}</div>
              {onRetry && (
                <button
                  onClick={onRetry}
                  aria-label="Retry message"
                  className="mt-2 px-3 py-1 bg-blue-500 text-white rounded-full hover:bg-blue-600 transition"
                >
                  Retry
                </button>
              )}
            </>
          )}

          {/* Success */}
          {!error && !isLoading && (
            <div>
              {msg.content}
              {msg.role === "ai" &&
                (() => {
                  // Gather all references in a flat array
                  const allReferences = msg.response_parts.flatMap(
                    (part) => part.references
                  );
                  if (allReferences.length === 0) return null;
                  return (
                    <div className="mt-2 flex gap-1 flex-wrap">
                      <div className="font-bold mb-1">Sources:</div>
                      <div>
                        {allReferences.map((reference, i) => (
                          <a
                            key={i}
                            href={reference.url}
                            target="_blank"
                            rel="noopener noreferrer"
                            className="text-blue-600 dark:text-blue-400 no-underline ml-0.5"
                          >
                            [{i + 1}]
                          </a>
                        ))}
                      </div>
                    </div>
                  );
                })()}
            </div>
          )}

          {/* Timestamp */}
          {formattedTime && (
            <div className="text-right text-xs text-gray-400 dark:text-gray-500 mt-1">
              {formattedTime}
            </div>
          )}
        </div>

        {/* 3-dots trigger */}
        {msg.role === "ai" && !isLoading && !error && (
          <>
            <button
              onClick={(e) => {
                e.stopPropagation();
                setMenuOpen(true);
              }}
              className="p-1 ml-1 rounded-full hover:bg-gray-200/70 dark:hover:bg-gray-600"
              aria-haspopup="dialog"
              aria-expanded={menuOpen}
              aria-label="Message options"
            >
              <svg
                xmlns="http://www.w3.org/2000/svg"
                fill="currentColor"
                viewBox="0 0 20 20"
                className="w-5 h-5 text-gray-500 dark:text-gray-300"
              >
                <path d="M6 10a2 2 0 11-4 0 2 2 0 014 0zm6 0a2 2 0 11-4 0 2 2 0 014 0zm6 0a2 2 0 11-4 0 2 2 0 014 0z" />
              </svg>
            </button>

            {/* Centered popup (restyled) */}
            {menuOpen && (
              <div className="fixed inset-0 z-50">
                {/* Backdrop with blur */}
                <div
                  className="absolute inset-0 bg-black/30 backdrop-blur-[2px]"
                  aria-hidden="true"
                />
                <div className="absolute inset-0 flex items-end sm:items-center justify-center p-4">
                  <div
                    ref={menuRef}
                    role="dialog"
                    aria-modal="true"
                    aria-label="Message options"
                    className="w-full max-w-sm rounded-2xl bg-white/95 dark:bg-gray-800/95 shadow-xl border border-gray-200/70 dark:border-gray-700/60
                               transition-all duration-150 ease-out
                               animate-[fadeIn_120ms_ease-out] sm:animate-[pop_140ms_ease-out]"
                    style={{
                      // keyframes in inline style fallback
                      // fadeIn: opacity in; pop: scale + opacity in
                      animationName: undefined,
                    }}
                  >
                    {/* Header */}
                    <div className="px-5 py-3 border-b border-gray-200/70 dark:border-gray-700/60">
                      <div className="text-sm font-semibold text-gray-900 dark:text-gray-100">
                        Message options
                      </div>
                      <div className="text-xs text-gray-500 dark:text-gray-400">
                        Quick actions for this AI reply
                      </div>
                    </div>

                    {/* Actions */}
                    <div className="p-2">
                      <button
                        onClick={handleGiveFeedback}
                        className="w-full flex items-center gap-3 px-4 py-3 rounded-xl
                                   text-sm text-gray-800 dark:text-gray-100
                                   hover:bg-gray-100 dark:hover:bg-gray-700
                                   active:scale-[0.99] transition"
                      >
                        {/* chat-bubble-heart icon */}
                        <span className="inline-flex items-center justify-center w-7 h-7 rounded-lg bg-indigo-50 text-indigo-600 dark:bg-indigo-900/40 dark:text-indigo-300">
                          <svg
                            viewBox="0 0 24 24"
                            className="w-4 h-4"
                            fill="currentColor"
                          >
                            <path d="M12 21s-6.716-3.873-9.193-7.35C1.083 11.426 2.2 8 5.5 8c1.9 0 2.887 1.087 3.5 2 .613-.913 1.6-2 3.5-2 3.3 0 4.417 3.426 2.693 5.65C18.716 17.127 12 21 12 21z" />
                          </svg>
                        </span>
                        <div className="flex-1 text-left">
                          <div className="font-medium">Give feedback</div>
                          <div className="text-xs text-gray-500 dark:text-gray-400">
                            Report issues or share thoughts
                          </div>
                        </div>
                      </button>

                      <button
                        onClick={handleCopy}
                        className="mt-1 w-full flex items-center gap-3 px-4 py-3 rounded-xl
                                   text-sm text-gray-800 dark:text-gray-100
                                   hover:bg-gray-100 dark:hover:bg-gray-700
                                   active:scale-[0.99] transition"
                      >
                        {/* copy icon */}
                        <span className="inline-flex items-center justify-center w-7 h-7 rounded-lg bg-gray-100 text-gray-700 dark:bg-gray-700/60 dark:text-gray-200">
                          <svg
                            viewBox="0 0 24 24"
                            className="w-4 h-4"
                            fill="currentColor"
                          >
                            <path d="M8 7a2 2 0 012-2h7a2 2 0 012 2v9a2 2 0 01-2 2h-7a2 2 0 01-2-2V7zm-3 3a2 2 0 012-2v9a4 4 0 004 4h7a2 2 0 002-2h-9a4 4 0 01-4-4V10z" />
                          </svg>
                        </span>
                        <div className="flex-1 text-left">
                          <div className="font-medium">Copy message</div>
                          <div className="text-xs text-gray-500 dark:text-gray-400">
                            Copy the full AI response
                          </div>
                        </div>
                      </button>
                    </div>

                    {/* Footer */}
                    <div className="px-5 py-3 border-t border-gray-200/70 dark:border-gray-700/60 flex justify-end">
                      <button
                        onClick={() => setMenuOpen(false)}
                        className="px-3 py-1.5 rounded-xl border border-gray-300 dark:border-gray-600
                                   text-sm hover:bg-gray-50 dark:hover:bg-gray-700"
                      >
                        Close
                      </button>
                    </div>
                  </div>
                </div>
              </div>
            )}
          </>
        )}
      </div>
    </div>
  );
};

export default ChatBubble;
