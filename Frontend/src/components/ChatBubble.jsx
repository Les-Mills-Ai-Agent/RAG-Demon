import React from 'react'

export default function ChatBubble({ msg, onRetry }) {
  const base =
    'max-w-[80%] px-4 py-3 rounded-2xl whitespace-pre-wrap text-sm shadow-sm'

  const classes =
    msg.role === 'user'
      ? `${base} bg-blue-100 text-gray-800 self-end`
      : `${base} ${
          msg.status === 'error'
            ? 'bg-red-100 text-red-700'
            : 'bg-gray-100 text-gray-800'
        } self-start`

  if (msg.role === 'system') {
    return (
      <div className="text-sm italic text-gray-500 text-center my-4">
        {msg.content}
      </div>
    )
  }

  return (
    <div className={`w-full flex ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}>
      <div className={classes}>
        {msg.status === 'loading' && <em>Loading…</em>}
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
        {msg.status === 'success' && msg.content}
        {!msg.status && msg.content}
      </div>
    </div>
  )
}
