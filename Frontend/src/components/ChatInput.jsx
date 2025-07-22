import React, { useState } from 'react'

export default function ChatInput({ onSend }) {
  const [text, setText] = useState('')

  const submit = e => {
    e.preventDefault()
    const trimmed = text.trim()
    if (!trimmed) return
    onSend(trimmed)
    setText('')
  }

  return (
    <form onSubmit={submit} className="flex items-center border-t p-2 gap-2">
      <button type="button">📎</button>
      <input
        className="flex-1 border rounded px-3 py-2 focus:outline-none"
        placeholder="Ask me anything about Les Mills..."
        value={text}
        onChange={e => setText(e.target.value)}
      />
      <button
        type="submit"
        className="bg-blue-500 text-white px-4 py-2 rounded"
      >➤</button>
    </form>
  )
}
