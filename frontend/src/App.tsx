import React, { useState, useEffect } from 'react';
import ChatWindow from './components/ChatWindow';
import ChatInput from './components/ChatInput';
import { getChatCompletion } from './utils/openai';
import './index.css';
import { v4 as uuidv4 } from 'uuid';
import { Message } from './types/message.ts';
import { useAuth } from 'react-oidc-context';            

export default function App() {
  const [messages, setMessages] = useState<Message[]>([
    {
      id: uuidv4(),
      role: 'system',
      content: "Hi! I'm your Les Mills AI assistant. I'm here to help you with B2B inquiries, solutions, and anything else Les Mills related. How can I assist you today?",
      status: 'success',
      createdAt: new Date().toISOString(),
    },
  ]);

  const [darkMode, setDarkMode] = useState<boolean>(false);

  useEffect(() => {
    document.documentElement.classList.toggle('dark', darkMode);
  }, [darkMode]);

  const append = (msg: Message) => setMessages((ms) => [...ms, msg]);

  const sendMessage = async (text: string) => {
    const trimmed = text.trim();
    if (!trimmed) return; // Input validation

    const userMessage: Message = {
      id: uuidv4(),
      role: 'user',
      content: trimmed,
      status: 'success',
      createdAt: new Date().toISOString(),
    };

    const placeholderId = uuidv4();
    const placeholder: Message = {
      id: placeholderId,
      role: 'assistant',
      content: '',
      status: 'loading',
      createdAt: new Date().toISOString(),
    };

    append(userMessage);
    append(placeholder);

    try {
      const reply = await getChatCompletion([...messages, userMessage]);
      setMessages((ms) =>
        ms.map((m) =>
          m.id === placeholderId
            ? {
              ...m,
              content: reply,
              status: 'success',
              createdAt: new Date().toISOString(),
            }
            : m
        )
      );
    } catch (err) {
      setMessages((ms) =>
        ms.map((m) =>
          m.id === placeholderId
            ? {
              ...m,
              content: '',
              status: 'error',
              error: 'Something went wrong. Please try again.',
              createdAt: new Date().toISOString(),
            }
            : m
        )
      );
      console.error('Error fetching chat completion:', err); // Still log internally
    }
  };

  const handleRetry = () => {
    const lastUser = [...messages].reverse().find((m) => m.role === 'user');
    if (lastUser) sendMessage(lastUser.content);
  };

  // ---------- AUTH GATE (ADDED) ----------
  const auth = useAuth();                                     
  if (auth.isLoading) {                                      
    return <div className="p-4">Loading…</div>;               
  }                                                           
  if (auth.error) {                                           
    return <div className="p-4">Error: {auth.error.message}</div>; 
  }                                                           
  if (!auth.isAuthenticated) {                                
    return (                                                  
      <div className="min-h-screen flex items-center justify-center p-6">  {}
        <button                                             
          onClick={() => auth.signinRedirect()}               
          className="px-4 py-2 rounded bg-black text-white dark:bg-white dark:text-black" 
        >                                                    
          Sign in with Cognito                                
        </button>                                            
      </div>                                                  
    );                                                        
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

          {}
          <span className="text-sm text-gray-600 dark:text-gray-300">
            {auth.user?.profile?.email}
          </span>
          <button
            onClick={() => auth.signoutRedirect()}
            className="text-sm px-3 py-1 rounded bg-gray-900 text-white dark:bg-gray-200 dark:text-gray-900"
          >
            Sign out
          </button>
          {/* ------------------------------- */}
        </div>
      </header>

      <main className="flex-1 overflow-y-auto px-4 sm:px-6 py-4">
        <ChatWindow messages={messages} onRetry={handleRetry} />
      </main>

      <footer className="bg-white dark:bg-gray-800 shadow-inner border-t dark:border-gray-700 px-4 py-3">
        <ChatInput onSend={sendMessage} />
      </footer>
    </div>
  );
}
