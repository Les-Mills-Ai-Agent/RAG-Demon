import React, { useState } from 'react'

export default function ChatInput({ onSend }) {
  const [text, setText] = useState('')
  const [error, setError] = useState(false)

  const submit = (e) => {
    e.preventDefault()
    const trimmed = text.trim()
    if (!trimmed) {
      setError(true)
      return
    }

    onSend(trimmed)
    setText('')
    setError(false)
  }

  return (
    <>
      <form
        onSubmit={submit}
        className={`w-full max-w-3xl mx-auto flex items-center gap-3 bg-white border ${
          error ? 'border-red-500' : 'border-gray-300'
        } rounded-full px-4 py-2 shadow transition-all duration-200`}
      >
        <input
          type="text"
          className="flex-1 text-sm text-gray-800 placeholder-gray-400 bg-transparent focus:outline-none"
          placeholder="Ask anything..."
          value={text}
          onChange={(e) => {
            setText(e.target.value)
            if (error) setError(false)
          }}
        />
        <button
          type="submit"
          className="text-white bg-blue-500 hover:bg-blue-600 px-4 py-2 rounded-full transition text-sm font-semibold"
        >
          ➤
        </button>
      </form>
      {error && (
        <p className="text-sm text-red-500 text-center mt-1">
          Please enter a valid message.
        </p>
      )}
    </>
  )
}
