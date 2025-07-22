import React from 'react'
import ChatBubble from './ChatBubble.jsx'

export default function ChatWindow({ messages, onRetry }) {
  return (
    <div className="flex-1 overflow-y-auto p-4 flex flex-col gap-2">
      {messages.map((m, i) => (
        <ChatBubble key={i} msg={m} onRetry={() => onRetry(i)} />
      ))}
    </div>
  )
}
