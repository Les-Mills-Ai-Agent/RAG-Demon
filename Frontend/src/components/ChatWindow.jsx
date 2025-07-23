import React from 'react'
import ChatBubble from './ChatBubble.jsx'

export default function ChatWindow({ messages, onRetry }) {
  return (
    <div className="flex flex-col gap-4 max-w-4xl mx-auto">
      {messages.map((m, i) => (
        <ChatBubble key={i} msg={m} onRetry={() => onRetry(i)} />
      ))}
    </div>
  )
}
