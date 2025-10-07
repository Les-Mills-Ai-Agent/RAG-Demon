import { QueryClientProvider } from "@tanstack/react-query";
import { queryClient } from "./queryClient";
import React, { useState, useEffect, useRef } from "react";
import ChatWindow from "./components/ChatWindow";
import ChatInput from "./components/ChatInput";
import "./index.css";
import { v4 as uuidv4 } from "uuid";
import { useAuth } from "react-oidc-context";
import LoginCelebration from "./components/LoginCelebration";
import ConfirmSignOut from "./components/ConfirmSignOut";
import EngineSwitcher from "./components/EngineSwitcher";
import SlidingPanel from "./components/SlidingPanel";
import { getConversations, getMessages, Conversation, Message } from "./utils/api";

export default function App() {
  const [isPanelOpen, setIsPanelOpen] = useState(false);
  const [darkMode, setDarkMode] = useState<boolean>(false);

  const [conversations, setConversations] = useState<Conversation[]>([]);
  const [messages, setMessages] = useState<Message[]>([]);
  const [activeSession, setActiveSession] = useState<string | null>(null);

  useEffect(() => {
    document.documentElement.classList.toggle("dark", darkMode);
  }, [darkMode]);

  const [engine, setEngine] = useState<"openai" | "bedrock">("openai");


  // ---------- AUTH ----------
  const auth = useAuth();

  // Celebration state
  const [showCelebrate, setShowCelebrate] = useState(false);
  const wasAuthed = useRef(false);

  // Sign-out confirmation modal state
  const [showSignoutConfirm, setShowSignoutConfirm] = useState(false);
  const onSignoutConfirm = async () => {
    // one-time flag: skip celebration on the very next login
    sessionStorage.setItem("skipNextLoginCelebrate", "1");

    const postLogout = window.location.origin + "/signed-out";

    await auth.signoutRedirect({
      post_logout_redirect_uri: postLogout,
      extraQueryParams: {
        client_id: import.meta.env.VITE_COGNITO_CLIENT_ID as string,
        logout_uri: postLogout,
      },
    });
  };

  // Auto-login when not authenticated
  useEffect(() => {
    const path = window.location.pathname;
    const onCallback = path.startsWith("/callback");
    const onSignedOut = path.startsWith("/signed-out");
    if (
      !auth.isLoading &&
      !auth.isAuthenticated &&
      !auth.activeNavigator &&
      !onCallback &&
      !onSignedOut
    ) {
      auth.signinRedirect({ prompt: "login" });
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

  useEffect(() => {
    const loadConversations = async () => {
      if (auth.isAuthenticated && auth.user?.profile?.sub) {
        try {
          const convos = await getConversations(auth.user.profile.sub);
          setConversations(convos);
        } catch (err) {
          console.error("Failed to load conversations", err);
        }
      }
    };
    loadConversations();
  }, [auth.isAuthenticated, auth.user]);

  // 🔸 Handle selecting a conversation
  const handleSelectConversation = async (sessionId: string) => {
    setActiveSession(sessionId);
    setIsPanelOpen(false);
    try {
      const msgs = await getMessages(sessionId);
      setMessages(msgs);
    } catch (err) {
      console.error("Failed to load messages", err);
    }
  };

  // Early returns AFTER all hooks are declared
  if (auth.isLoading || auth.activeNavigator)
    return <div className="p-4">Loading…</div>;
  if (auth.error) return <div className="p-4">Error: {auth.error.message}</div>;

  // If we're on /signed-out and unauthenticated, bounce to login
  if (!auth.isAuthenticated) {
    const onSignedOut = window.location.pathname.startsWith("/signed-out");
    if (onSignedOut) {
      auth.signinRedirect({ prompt: "login" });
      return <div className="p-4">Redirecting to login…</div>;
    }
    return null;
  }
  
  return (
    <div className="flex flex-col h-screen bg-gray-50 dark:bg-gray-900 text-gray-800 dark:text-gray-100 font-sans transition-colors duration-300">
      <LoginCelebration
        visible={showCelebrate}
        userEmail={auth.user?.profile?.email || "User"}
      />

      <ConfirmSignOut
        open={showSignoutConfirm}
        onCancel={() => setShowSignoutConfirm(false)}
        onConfirm={onSignoutConfirm}
      />
      {/*Side Panel*/}
      <SlidingPanel
        isOpen={isPanelOpen}
        onClose={() => setIsPanelOpen(false)}
        title="Conversations"
      >
        <ul>
          {conversations.length === 0 && (
            <li className="p-3 text-gray-500">No conversations yet</li>
          )}
          {conversations.map((c) => (
            <li
              key={c.session_id}
              className="p-3 hover:bg-gray-100 dark:hover:bg-gray-700 cursor-pointer"
              onClick={() => handleSelectConversation(c.session_id)}
            >
              {new Date(c.last_updated).toLocaleString()}
            </li>
          ))}
        </ul>
      </SlidingPanel>

      <header className="bg-white dark:bg-gray-800 px-6 py-4 shadow-md flex items-center justify-between border-b dark:border-gray-700">
        <div className="flex items-center gap-4">

          <button
            onClick={() => setIsPanelOpen(true)}
            className="px-2 py-1 rounded hover:bg-gray-100 dark:hover:bg-gray-700"
          >=</button>
        <h1 className="text-xl font-bold text-gray-800 dark:text-white">
          Les Mills AI Assistant
        </h1>
        </div>

        <div className="flex items-center gap-4">

           <EngineSwitcher value={engine} onChange={setEngine} /> {/* NEW */}
          <button
            onClick={() => setDarkMode(!darkMode)}
            className="text-sm px-3 py-1 rounded-full border dark:border-gray-600 bg-gray-100 dark:bg-gray-700 text-gray-700 dark:text-gray-100 hover:shadow transition"
          >
            {darkMode ? "🌙 Dark" : "☀️ Light"}
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
        <QueryClientProvider client={queryClient}>
          <ChatWindow
            backendImpl={engine === "bedrock" ? "bedrock" : "langchain"}
          />
        </QueryClientProvider>
      </main>

    </div>
  );
}
