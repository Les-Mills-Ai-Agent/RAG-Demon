import React from 'react'

export default function ChatBubble({ msg, onRetry }) {
  const base = "max-w-[80%] px-4 py-2 rounded-lg whitespace-pre-wrap"
  if (msg.role === 'system') {
    return (
      <div className="text-sm italic text-gray-500 text-center my-4">
        {msg.content}
      </div>
    )
  }
  const classes = msg.role === 'user'
    ? `${base} bg-blue-100 self-end`
    : `${base} ${msg.status === 'error' ? 'bg-red-100' : 'bg-gray-100'} self-start`

  return (
    <div className={classes}>
      {msg.status === 'loading' && <em>Loading…</em>}
      {msg.status === 'error' && (
        <>
          <div>⚠️ {msg.error}</div>
          <button
            onClick={onRetry}
            className="mt-2 px-3 py-1 bg-blue-500 text-white rounded"
          >Retry</button>
        </>
      )}
      {msg.status === 'success' && msg.content}
      {!msg.status && msg.content}
    </div>
  )
}
