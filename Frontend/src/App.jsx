import React, { useState } from 'react'
import ChatWindow from './components/ChatWindow.jsx'
import ChatInput from './components/ChatInput.jsx'
import { getChatCompletion } from './utils/openai.js'
import './index.css'


export default function App() {
  const [messages, setMessages] = useState([
    {
      role: 'system',
      content: "Hi! I'm your Les Mills AI assistant. I'm here to help you with B2B inquiries, solutions, and anything else Les Mills related. How can I assist you today?"
    }
  ])

  const append = msg => setMessages(ms => [...ms, msg])

  const sendMessage = async text => {
    const userMessage = { role: 'user', content: text }
    const placeholder = { role: 'assistant', content: '', status: 'loading' }

    append(userMessage)
    append(placeholder)

    try {
      const reply = await getChatCompletion([...messages, userMessage])
      setMessages(ms => ms.map(m =>
        m === placeholder
          ? { role: 'assistant', content: reply, status: 'success' }
          : m
      ))
    } catch (err) {
      const detail = err.response?.data?.detail || err.message
      setMessages(ms => ms.map(m =>
        m === placeholder
          ? { role: 'assistant', content: '', status: 'error', error: detail }
          : m
      ))
    }
  }

  const handleRetry = () => {
    const lastUser = [...messages].reverse().find(m => m.role === 'user')
    if (lastUser) sendMessage(lastUser.content)
  }

  return (
    <div className="flex flex-col h-screen bg-gray-50 text-gray-800 font-sans">
      <header className="bg-white px-6 py-4 shadow-md flex items-center justify-between border-b">
        <h1 className="text-xl font-bold text-gray-800">Les Mills AI Assistant</h1>
        <div className="flex items-center space-x-2">
          <span className="h-3 w-3 bg-green-500 rounded-full animate-pulse" />
          <span className="text-sm text-gray-600">Online</span>
        </div>
      </header>

      <main className="flex-1 overflow-y-auto px-4 sm:px-6 py-4">
        <ChatWindow messages={messages} onRetry={handleRetry} />
      </main>

      <footer className="bg-white shadow-inner border-t px-4 py-3">
        <ChatInput onSend={sendMessage} />
      </footer>
    </div>
  )
}
