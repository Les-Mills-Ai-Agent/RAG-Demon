import React, { useState } from 'react'

export default function ChatInput({ onSend }) {
  const [text, setText] = useState('')

  const submit = (e) => {
    e.preventDefault()
    const trimmed = text.trim()
    if (!trimmed) return
    onSend(trimmed)
    setText('')
  }

  return (
    <form
      onSubmit={submit}
      className="w-full max-w-3xl mx-auto flex items-center gap-3 bg-white border border-gray-300 rounded-full px-4 py-2 shadow"
    >
      <input
        type="text"
        className="flex-1 text-sm text-gray-800 placeholder-gray-400 bg-transparent focus:outline-none"
        placeholder="Ask anything..."
        value={text}
        onChange={(e) => setText(e.target.value)}
      />
      <button
        type="submit"
        className="text-white bg-blue-500 hover:bg-blue-600 px-4 py-2 rounded-full transition text-sm font-semibold"
      >
        ➤
      </button>
    </form>
  )
}
