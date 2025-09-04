import React, { useState, useEffect } from "react";
import ChatWindow from "./components/ChatWindow";
import { QueryClientProvider } from "@tanstack/react-query";
import { queryClient } from "./queryClient";
import ChatInput from "./components/ChatInput";
import { getChatCompletion } from "./utils/openai";
import "./index.css";
import { v4 as uuidv4 } from "uuid";
// import { Message } from "./types/message";
import { UseQueryResult } from "@tanstack/react-query";
import {
  ErrorResponse,
  Message,
  RAGRequest,
  RAGResponse,
} from "./models/models";
import { useBedrock } from "./hooks/useBedrock";

type BackendImpl = "bedrock" | "langchain";

export default function App() {
  const [darkMode, setDarkMode] = useState<boolean>(false);

  useEffect(() => {
    document.documentElement.classList.toggle("dark", darkMode);
  }, [darkMode]);

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
            {darkMode ? "🌙 Dark" : "☀️ Light"}
          </button>
        </div>
      </header>

      <main className="flex-1 overflow-y-auto px-4 sm:px-6 py-4">
        <QueryClientProvider client={queryClient}>
          <ChatWindow />
        </QueryClientProvider>
      </main>
    </div>
  );
}
