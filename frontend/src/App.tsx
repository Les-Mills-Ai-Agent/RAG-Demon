import React, { useState, useEffect, useRef } from 'react';
import ChatWindow from './components/ChatWindow';
import ChatInput from './components/ChatInput';
import { getChatCompletion } from './utils/openai';
import './index.css';
import { v4 as uuidv4 } from 'uuid';
import { Message } from './types/message.ts';
import { useAuth } from 'react-oidc-context';
import LoginCelebration from './components/LoginCelebration';
import ConfirmSignOut from './components/ConfirmSignOut';

export default function App() {
  const [messages, setMessages] = useState<Message[]>([
    {
      id: uuidv4(),
      role: 'system',
      content:
        "Hi! I'm your Les Mills AI assistant. I'm here to help you with B2B inquiries, solutions, and anything else Les Mills related. How can I assist you today?",
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
    if (!trimmed) return;

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
      console.error('Error fetching chat completion:', err);
    }
  };

  const handleRetry = () => {
    const lastUser = [...messages].reverse().find((m) => m.role === 'user');
    if (lastUser) sendMessage(lastUser.content);
  };

  // ---------- AUTH ----------
  const auth = useAuth();

  // Celebration state
  const [showCelebrate, setShowCelebrate] = useState(false);
  const wasAuthed = useRef(false);

  // Sign-out confirmation modal state
  const [showSignoutConfirm, setShowSignoutConfirm] = useState(false);
  const onSignoutConfirm = () => {
    // one-time flag: skip celebration on the very next login
    sessionStorage.setItem('skipNextLoginCelebrate', '1');

    const authority = import.meta.env.VITE_COGNITO_AUTHORITY;
    const clientId  = import.meta.env.VITE_COGNITO_CLIENT_ID;
    const logoutUri = encodeURIComponent(window.location.origin + '/callback');

    window.location.href =
      `${authority}/logout?client_id=${clientId}&logout_uri=${logoutUri}`;
  };


  // Auto-login when not authenticated
  useEffect(() => {
    const onCallback = window.location.pathname.startsWith('/callback');
    if (
      !auth.isLoading &&
      !auth.isAuthenticated &&
      !auth.activeNavigator &&
      !onCallback
    ) {
      auth.signinRedirect();
    }
  }, [auth.isLoading, auth.isAuthenticated, auth.activeNavigator]);

  // Show celebration once per tab session after first successful auth
  useEffect(() => {
    if (auth.isAuthenticated && !wasAuthed.current) {
      wasAuthed.current = true;
      setShowCelebrate(true);
      const t = setTimeout(() => setShowCelebrate(false), 1600);
      return () => clearTimeout(t);
    }
  }, [auth.isAuthenticated]);

  // Early returns AFTER all hooks are declared
  if (auth.isLoading || auth.activeNavigator)
    return <div className="p-4">Loading…</div>;
  if (auth.error) return <div className="p-4">Error: {auth.error.message}</div>;
  if (!auth.isAuthenticated) return null;

  return (
    <div className="flex flex-col h-screen bg-gray-50 dark:bg-gray-900 text-gray-800 dark:text-gray-100 font-sans transition-colors duration-300">
      <LoginCelebration
        visible={showCelebrate}
        userEmail={auth.user?.profile?.email || 'User'}
      />

      <ConfirmSignOut
        open={showSignoutConfirm}
        onCancel={() => setShowSignoutConfirm(false)}
        onConfirm={onSignoutConfirm}
      />

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

          <span className="text-sm text-gray-600 dark:text-gray-300">
            {auth.user?.profile?.email}
          </span>
          <button
            onClick={() => setShowSignoutConfirm(true)}
            className="text-sm px-3 py-1 rounded bg-gray-900 text-white dark:bg-gray-200 dark:text-gray-900"
          >
            Sign out
          </button>
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
