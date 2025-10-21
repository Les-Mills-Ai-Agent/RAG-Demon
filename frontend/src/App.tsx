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
import { FeedbackProvider } from "./components/FeedbackProvider";
import SlidingPanel from "./components/SlidingPanel";
import { getConversations, getMessages, Conversation, Message, deleteConversation } from "./utils/api";
import Popup from "./components/Popup";

export default function App() {
  const [isPanelOpen, setIsPanelOpen] = useState(false);
  const [darkMode, setDarkMode] = useState<boolean>(false);

  const [conversations, setConversations] = useState<Conversation[]>([]);
  const [activeSession, setActiveSession] = useState<string | null>(null);
  const [hoveredId, setHoveredId] = useState<string | null>(null);
  const [popupId, setPopupId] = useState<string | null>(null);

  const [viewingConversation, setViewingConversation] = useState<Message[] | undefined>(undefined);

  useEffect(() => {
    document.documentElement.classList.toggle("dark", darkMode);
  }, [darkMode]);

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
          const convos = await getConversations(auth.user.profile.sub, auth.user.id_token!);
          const sortedConvos = convos.sort((a, b) => {
            return new Date(b.last_updated).valueOf() - new Date (a.last_updated).valueOf()
          })
          setConversations(sortedConvos);
        } catch (err) {
          console.error("Failed to load conversations", err);
          console.log(auth.user?.profile?.sub)
          console.log(auth.user?.id_token)
        }
      }
    };
    loadConversations();
  }, [auth.isAuthenticated, auth.user]);

  const handleSelectConversation = async (sessionId: string) => {
    setActiveSession(sessionId);

    const cleanSessionId = sessionId.replace(/^SESSION#SESSION#/, "SESSION#");
    const encodeSessionID = encodeURIComponent(cleanSessionId);

    if (auth.isAuthenticated && auth.user?.profile.sub) {
      try {
        const msgs = await getMessages(encodeSessionID, auth.user.id_token!);

        const formattedMessages: Message[] = msgs.map((m: any) => {
          const match = m.created_at_message_id.match(/^MESSAGE#([^#]+)#/);
          const timestamp = match ? match[1] : new Date().toISOString(); 

          return {
            message_id: m.created_at_message_id,
            content: m.body,
            response_parts: m.response_parts ?? [],
            session_id: m.session_id,
            created_at: timestamp, 
            role: m.role,
          };
        });
        setViewingConversation(formattedMessages);

      } catch (err) {
        console.error("Failed to load messages", err);
      }
    }
  };

  const handleDeleteConversation = async (sessionId: string) => {
    const cleanSessionId = sessionId.replace(/^SESSION#SESSION#/, "SESSION#");
    const encodeSessionID = encodeURIComponent(cleanSessionId);
    console.log("id about to be deleted: "+cleanSessionId)

      // try {
      //   const response = await deleteConversation(encodeSessionID, auth.user.id_token!)
        
      // } catch (error) {
      //   console.error("Failed to delete conversation", error);
      //   return;
      // }
      setConversations(conversations.filter(convo => {
        return convo.session_id !== sessionId
      }));
  
      if (activeSession === popupId) {
        setViewingConversation(undefined);
        setActiveSession(null);
        setHoveredId(null);
      }
  
      setPopupId(null);
  }

  console.log("active session id:" + activeSession);

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
    <div className="flex flex-col min-h-screen bg-gray-50 dark:bg-gray-900 text-gray-800 dark:text-gray-100 font-sans transition-colors duration-300">
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
              className={`flex items-center justify-between p-3 cursor-pointer ${c.session_id === activeSession ? 'bg-gray-100 dark:bg-gray-700' : 'hover:bg-gray-50 dark:hover:bg-gray-600'} rounded-2xl`}
              onClick={() => handleSelectConversation(c.session_id)}
              onMouseEnter={() => setHoveredId(c.session_id)}
              onMouseLeave={() => setHoveredId(null)}
            >
              <span>{new Date(c.last_updated).toLocaleString()}</span>
              {(hoveredId === c.session_id || activeSession === c.session_id) && 
                <>
                  <span 
                    className="p-1 text-gray-500 dark:text-gray-300 hover:text-red-500 hover:dark:text-red-500 hover:bg-gray-200 dark:hover:bg-gray-600 rounded-full"
                    onClick={(e) => {
                      e.stopPropagation();
                      setPopupId(c.session_id)
                    }}
                  >
                    <svg 
                      className="w-4 h-4" 
                      aria-hidden="true" xmlns="http://www.w3.org/2000/svg" width="24" height="24" fill="none" viewBox="0 0 24 24">
                      <path stroke="currentColor" strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M5 7h14m-9 3v8m4-8v8M10 3h4a1 1 0 0 1 1 1v3H9V4a1 1 0 0 1 1-1ZM6 7h12v13a1 1 0 0 1-1 1H7a1 1 0 0 1-1-1V7Z"/>
                    </svg>
                  </span>
                  {popupId === c.session_id &&
                    <Popup 
                      title="Delete conversation"
                      description="Are you sure you want to delete this conversation?"
                      action="Delete"
                      onSuccess={() => handleDeleteConversation(c.session_id)}
                      onClose={() => setPopupId(null)}
                    />
                  }
                </>
              }
            </li>
          ))}
        </ul>
      </SlidingPanel>

      <header className="sticky top-0 z-10 bg-white/90 dark:bg-gray-800/90 backdrop-blur supports-[backdrop-filter]:bg-white/85 dark:supports-[backdrop-filter]:bg-gray-800/85 px-6 py-4 shadow-md flex items-center justify-between border-b dark:border-gray-700">
        <div className="flex items-center gap-4">

          <button
            onClick={() => setIsPanelOpen(prev => !prev)}
            className="px-2 py-1 rounded hover:bg-gray-100 dark:hover:bg-gray-700"
          >=</button>
        <h1 className="text-xl font-bold text-gray-800 dark:text-white">
          Les Mills AI Assistant
        </h1>
        </div>

        <div className="flex items-center gap-4">
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

      {/* Wider centred chat container */}
      <main className="flex-1">
        <div className="mx-auto w-full max-w-5xl px-6 py-6 flex flex-col">
          <QueryClientProvider client={queryClient}>
            <FeedbackProvider>
              <ChatWindow
                messages={viewingConversation ? viewingConversation : undefined} 
              />
            </FeedbackProvider>
          </QueryClientProvider>
        </div>
      </main>
    </div>
  );
}
