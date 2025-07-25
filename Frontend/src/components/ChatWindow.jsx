import React, { useEffect, useRef } from 'react'
import ChatBubble from './ChatBubble.jsx'

export default function ChatWindow({ messages, onRetry }) {
  const bottomRef = useRef(null)

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages])

  return (
    <div className="flex flex-col gap-4 max-w-4xl mx-auto">
      {messages.map((m) => (
        <ChatBubble key={m.id} msg={m} onRetry={() => onRetry(m.id)} />
      ))}
      <div ref={bottomRef} />
    </div>
  )
}
