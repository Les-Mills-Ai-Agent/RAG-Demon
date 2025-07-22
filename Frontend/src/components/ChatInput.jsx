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
  <form
    onSubmit={submit}
    className="w-full flex justify-center px-4 pb-6 pt-2 sticky bottom-0 bg-transparent z-10"
  >
    <div className="w-full max-w-3xl flex items-center gap-2 bg-white rounded-2xl shadow-lg px-4 py-3 border border-gray-200">
      <button
        type="button"
        className="text-xl text-gray-400 hover:text-blue-500 transition"
      >
        📎
      </button>
      <input
        className="flex-1 text-sm text-gray-800 placeholder-gray-400 bg-transparent focus:outline-none"
        placeholder="Ask anything..."
        value={text}
        onChange={e => setText(e.target.value)}
      />
      <button
        type="submit"
        className="text-white bg-blue-500 hover:bg-blue-600 px-3 py-2 rounded-full transition text-sm font-medium"
      >
        ➤
      </button>
    </div>
  </form>
)

}
