import React, { useState } from "react";
import ReactMarkdown from "react-markdown";
import dayjs from "dayjs";
import { Message, AiMessage, ErrorResponse } from "../models/models";

interface ChatBubbleProps {
  msg: Message;
  isLoading: boolean;
  error: ErrorResponse | null;
  onRetry?: () => void;
}

const ChatBubble: React.FC<ChatBubbleProps> = ({
  msg,
  isLoading,
  error,
  onRetry,
}) => {
  const base =
    "max-w-[70%] px-4 py-3 rounded-2xl whitespace-pre-wrap text-sm shadow-sm animate-fadeIn";

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
      </div>
    </div>
  );
};

export default ChatBubble;
