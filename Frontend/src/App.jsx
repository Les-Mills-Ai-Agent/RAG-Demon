import React, { useState } from 'react'
import ChatWindow from './components/ChatWindow.jsx'
import ChatInput from './components/ChatInput.jsx'
import { getChatCompletion } from './utils/openai.js'

export default function App() {
  const [messages, setMessages] = useState([
    {
      role: 'system',
      content: "Hi! I'm your Les Mills AI assistant. I'm here to help you with B2B inquiries, and solutitons, and anything else Les Mills related. How can I assist you today?"
    }
  ])

  const append = msg => setMessages(ms => [...ms, msg])

  const sendMessage = async text => {
    append({ role: 'user', content: text })
    const placeholder = { role: 'assistant', content: '', status: 'loading' }
    append(placeholder)

    try {
      const reply = await getChatCompletion([...messages, { role: 'user', content: text }])
      setMessages(ms => ms.map(m =>
        m === placeholder
          ? { role: 'assistant', content: reply, status: 'success' }
          : m
      ))
    } catch (err) {
      const detail = err.response?.data?.detail || err.message
      console.error("Chat error:", detail)
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
    <div className="flex flex-col h-screen">
      <header className="bg-white p-4 shadow flex items-center">
        <h1 className="text-xl font-semibold">Les Mills AI Assistant</h1>
        <div className="ml-auto text-green-500">● Online</div>
      </header>

      <ChatWindow messages={messages} onRetry={handleRetry} />

      <ChatInput onSend={sendMessage} />
    </div>
  )
}
