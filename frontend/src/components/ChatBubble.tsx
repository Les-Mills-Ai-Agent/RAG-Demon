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
    "relative max-w-[70%] px-4 py-3 rounded-2xl whitespace-pre-wrap text-sm shadow-sm animate-fadeIn";

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
    window.addEventListener("click", onClick);
    return () => window.removeEventListener("click", onClick);
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
      className={`w-full flex ${msg.role === "user" ? "justify-end" : "justify-start"}`}
    >
      <div className="flex items-end gap-2">
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

          {/* Success (markdown response) */}
          {!error && !isLoading && (
            <div>
              {msg.role === "user" && msg.content}

              {msg.role === "ai" &&
                msg.response_parts.map((part, i) => (
                  <div key={i}>
                    <div className="prose prose-sm max-w-none dark:prose-invert">
                      {part.text}
                    </div>

                    {part.references.length > 0 &&
                      part.references.map((reference, j) => (
                        <a
                          href={reference.url}
                          target="_blank" // Opens in new tab
                          rel="noopener noreferrer" // Security shit
                          className="text-blue-600 dark:text-blue-400 no-underline ml-0.5"
                        >
                          [{j + 1}]
                        </a>
                      ))}
                  </div>
                ))}
            </div>
          )}

          {/* Timestamp */}
          {formattedTime && (
            <div className="text-right text-xs text-gray-400 dark:text-gray-500 mt-1">
              {formattedTime}
            </div>
          )}
        </div>

        {/* Three-dots menu: OUTSIDE the bubble, bottom-right, AI only */}
        {msg.role === "ai" && !isLoading && !error && (
          <div ref={menuRef} className="relative self-end">
            <button
              onClick={(e) => {
                e.stopPropagation();
                setMenuOpen((o) => !o);
              }}
              className="p-1 ml-1 rounded-full hover:bg-gray-200/70 dark:hover:bg-gray-600"
              aria-haspopup="menu"
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

            {menuOpen && (
              <div
                role="menu"
                className="absolute right-0 mt-2 w-44 origin-top-right rounded-md bg-white dark:bg-gray-800 shadow-lg border border-gray-200 dark:border-gray-700 z-10"
              >
                <button
                  onClick={handleGiveFeedback}
                  className="block w-full text-left px-4 py-2 text-sm text-gray-700 dark:text-gray-100 hover:bg-gray-50 dark:hover:bg-gray-700"
                  role="menuitem"
                >
                  Give feedback
                </button>
                <button
                  onClick={handleCopy}
                  className="block w-full text-left px-4 py-2 text-sm text-gray-700 dark:text-gray-100 hover:bg-gray-50 dark:hover:bg-gray-700"
                  role="menuitem"
                >
                  Copy message
                </button>
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  );
};

export default ChatBubble;
