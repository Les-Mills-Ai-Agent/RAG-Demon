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

export default function App() {
  const [darkMode, setDarkMode] = useState<boolean>(false);
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

      <header className="sticky top-0 z-40 bg-white/90 dark:bg-gray-800/90 backdrop-blur supports-[backdrop-filter]:bg-white/85 dark:supports-[backdrop-filter]:bg-gray-800/85 px-6 py-4 shadow-md flex items-center justify-between border-b dark:border-gray-700">
        <h1 className="text-xl font-bold text-gray-800 dark:text-white">
          Les Mills AI Assistant
        </h1>

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
              <ChatWindow/>
            </FeedbackProvider>
          </QueryClientProvider>
        </div>
      </main>
    </div>
  );
}
