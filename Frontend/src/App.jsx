import React, { useState, useEffect } from 'react'
import ChatWindow from './components/ChatWindow.jsx'
import ChatInput from './components/ChatInput.jsx'
import { getChatCompletion } from './utils/openai.js'
import './index.css'

export default function App() {
  const [messages, setMessages] = useState([
    {
      role: 'system',
      content:
        "Hi! I'm your Les Mills AI assistant. I'm here to help you with B2B inquiries, solutions, and anything else Les Mills related. How can I assist you today?",
      createdAt: new Date().toISOString(),
    },
  ])

  const [darkMode, setDarkMode] = useState(false)

  useEffect(() => {
    document.documentElement.classList.toggle('dark', darkMode)
  }, [darkMode])

  const append = (msg) => setMessages((ms) => [...ms, msg])

  const sendMessage = async (text) => {
    const userMessage = {
      role: 'user',
      content: text,
      createdAt: new Date().toISOString(),
    }
    const placeholder = {
      role: 'assistant',
      content: '',
      status: 'loading',
      createdAt: new Date().toISOString(),
    }

    append(userMessage)
    append(placeholder)

    try {
      const reply = await getChatCompletion([...messages, userMessage])
      setMessages((ms) =>
        ms.map((m) =>
          m === placeholder
            ? {
                role: 'assistant',
                content: reply,
                status: 'success',
                createdAt: new Date().toISOString(),
              }
            : m
        )
      )
    } catch (err) {
      const detail = err.response?.data?.detail || err.message
      setMessages((ms) =>
        ms.map((m) =>
          m === placeholder
            ? {
                role: 'assistant',
                content: '',
                status: 'error',
                error: detail,
                createdAt: new Date().toISOString(),
              }
            : m
        )
      )
    }
  }

  const handleRetry = () => {
    const lastUser = [...messages].reverse().find((m) => m.role === 'user')
    if (lastUser) sendMessage(lastUser.content)
  }

  return (
    <div className="flex flex-col h-screen bg-gray-50 dark:bg-gray-900 text-gray-800 dark:text-gray-100 font-sans transition-colors duration-300">
      <header className="bg-white dark:bg-gray-800 px-6 py-4 shadow-md flex items-center justify-between border-b dark:border-gray-700">
        <h1 className="text-xl font-bold text-gray-800 dark:text-white">
          Les Mills AI Assistant
        </h1>

        <div className="flex items-center gap-4">
          <button
            onClick={() => setDarkMode(!darkMode)}
            className="text-sm px-3 py-1 rounded-full border dark:border-gray-600 bg-gray-100 dark:bg-gray-700 text-gray-700 dark:text-gray-100 hover:shadow transition"
          >
            {darkMode ? '🌙 Dark' : '☀️ Light'}
          </button>

          <div className="flex items-center space-x-2">
            <span className="h-3 w-3 bg-green-500 rounded-full animate-pulse" />
            <span className="text-sm text-gray-600 dark:text-gray-300">Online</span>
          </div>
        </div>
      </header>

      <main className="flex-1 overflow-y-auto px-4 sm:px-6 py-4">
        <ChatWindow messages={messages} onRetry={handleRetry} />
      </main>

      <footer className="bg-white dark:bg-gray-800 shadow-inner border-t dark:border-gray-700 px-4 py-3">
        <ChatInput onSend={sendMessage} />
      </footer>
    </div>
  )
}
