import React from 'react'
import ReactMarkdown from 'react-markdown'
import dayjs from 'dayjs'

export default function ChatBubble({ msg, onRetry }) {
  const base =
    'max-w-[70%] px-4 py-3 rounded-2xl whitespace-pre-wrap text-sm shadow-sm animate-fadeIn'

  const classes =
    msg.role === 'user'
      ? `${base} bg-blue-100 text-gray-800 self-end dark:bg-blue-300 dark:text-black`
      : `${base} ${
          msg.status === 'error'
            ? 'bg-red-100 text-red-700 dark:bg-red-400'
            : 'bg-gray-100 text-gray-800 dark:bg-gray-700 dark:text-gray-100'
        } self-start`

  if (msg.role === 'system') {
    return (
      <div className="text-sm italic text-gray-500 text-center my-4">
        {msg.content}
      </div>
    )
  }

  const formattedTime = msg.createdAt
    ? dayjs(msg.createdAt).format('h:mm A')
    : null

  return (
    <div className={`w-full flex ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}>
      <div className="flex items-end gap-2">
        {/* Avatar for assistant */}
        {msg.role === 'assistant' && (
          <div className="bg-red-500 text-white rounded-full w-8 h-8 flex items-center justify-center text-sm font-bold shrink-0">
            LM
          </div>
        )}

        <div className={classes}>
          {/* Typing Animation */}
          {msg.status === 'loading' && (
            <div className="flex gap-1 text-gray-500">
              <span className="animate-blink delay-0">.</span>
              <span className="animate-blink delay-200">.</span>
              <span className="animate-blink delay-400">.</span>
            </div>
          )}

          {/* Error Message */}
          {msg.status === 'error' && (
            <>
              <div>⚠️ {msg.error}</div>
              <button
                onClick={onRetry}
                className="mt-2 px-3 py-1 bg-blue-500 text-white rounded-full hover:bg-blue-600 transition"
              >
                Retry
              </button>
            </>
          )}

          {/* Markdown message */}
          {msg.status === 'success' && msg.content && (
            <div className="prose prose-sm max-w-none dark:prose-invert">
              <ReactMarkdown>{msg.content}</ReactMarkdown>
            </div>
          )}

          {/* Raw fallback */}
          {!msg.status && msg.content}

          {/* Timestamp */}
          {formattedTime && (
            <div className="text-right text-xs text-gray-400 dark:text-gray-500 mt-1">
              {formattedTime}
            </div>
          )}
        </div>
      </div>
    </div>
  )
}
