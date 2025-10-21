import { useEffect, useRef, useState } from "react";
import ChatBubble from "./ChatBubble";
import { AiMessage, Message } from "../models/models";
import { useBedrock } from "../hooks/useBedrock";
import ChatInput from "./ChatInput";
import { UserMessage } from "../models/models";

type ChatWindowProps = {
  messages?: any[];
};

const ChatWindow = ({
  messages: externalMessages,
}: ChatWindowProps) => {
  const bottomRef = useRef<HTMLDivElement | null>(null);
  const [sessionId, setSessionId] = useState<string>();
  const [messages, setMessages] = useState<Message[]>(externalMessages || []);
  const [showScrollButton, setShowScrollButton] = useState(false); 
  const [readOnly, setReadOnly] = useState(false); // Flag to disable generating a response

  useEffect(() => {
    if (externalMessages) {
      setMessages(externalMessages);
      setSessionId(externalMessages[0].session_id.replace("SESSION#", ""));
      setReadOnly(true); // Stop app from trying to generate a response when viewing previous conversations
    } else if (externalMessages === undefined) {
      setMessages([]);
      setSessionId("");
      setReadOnly(true);
    }
  }, [externalMessages]);

  const lastUserMessage = messages.length > 0 ? {
    session_id: sessionId,
    ...(
      messages
        .slice()
        .reverse()
        .find((m) => m.role === "user")
    )
  } as UserMessage : undefined;

  const placeholderMessage: AiMessage = {
    message_id: "",
    content: "",
    response_parts: [],
    session_id: "",
    created_at: "",
    role: "ai",
  };

  const addMessage = (message: Message) => {
    if (readOnly) {
      setReadOnly(false);
    }
    setMessages((messages) => {
      // prevent duplicates
      if (messages.some((m) => m.message_id === message.message_id))
        return messages;
      return [...messages, message];
    });
  };

  const query = useBedrock(!readOnly ? lastUserMessage : undefined);

  useEffect(() => {
    if (query && query.isSuccess && query.data && !readOnly) {
      const aiMessage: AiMessage = {
        message_id: query.data.message_id,
        content: query.data.content,
        response_parts: query.data.response_parts,
        session_id: query.data.session_id,
        created_at: query.data.created_at,
        role: "ai",
      };
      setSessionId(query.data.session_id);
      addMessage(aiMessage);
    }
  }, [query?.data, query?.isSuccess, readOnly]);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  // Helper: find the nearest previous user message text before index `idx`
  //  Track scroll to toggle button visibility
  useEffect(() => {
    const handleScroll = () => {
      const distanceFromBottom =
        document.documentElement.scrollHeight -
        (window.scrollY + window.innerHeight);
      setShowScrollButton(distanceFromBottom > 250);
    };

    window.addEventListener("scroll", handleScroll, { passive: true });
    return () => window.removeEventListener("scroll", handleScroll);
  }, []);

  //  Scroll smoothly to bottom
  const scrollToBottom = () => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  // Helper
  const lastUserBefore = (idx: number): string => {
    for (let i = idx - 1; i >= 0; i--) {
      const m = messages[i];
      if (m && m.role === "user") return m.content ?? "";
    }
    return "";
  };

  const hasMessages = messages !== undefined && messages.length > 0;

  return (
    <div className="flex flex-col w-full min-h-[80vh]">
      {/* Landing (no messages yet) */}
      {!hasMessages ? (
        <div className="flex-1 flex flex-col items-center justify-center text-center gap-8 py-16">
          <h2 className="text-2xl sm:text-3xl font-semibold text-gray-700 dark:text-gray-200">
            Ask about the Les Mills content platform...
          </h2>

          {/* Input box - transparent background */}
          <div className="w-full max-w-2xl">
            <div className="bg-transparent">
              <ChatInput
                onSubmit={addMessage}
                disabled={query ? query.isLoading : false}
                session_id={sessionId}
              />
            </div>
          </div>
        </div>
      ) : (
        <>
          {/* Normal chat view */}
          <div className="flex-1 flex flex-col gap-4 pb-36">
            {messages.map((message, idx) => (
              <ChatBubble
                key={message.message_id}
                msg={message}
                isLoading={false}
                error={null}
                lastUserText={
                  message.role === "ai" ? lastUserBefore(idx) : undefined
                }
              />
            ))}
            {(!readOnly && query && (query.isLoading || query.error)) && (
              <ChatBubble
                msg={placeholderMessage}
                isLoading={query.isLoading}
                error={query.error}
                onRetry={query.refetch}
              />
            )}
            <div ref={bottomRef} />
          </div>

          {/* Sticky input with disclaimer below */}
          <div className="sticky bottom-0 left-0 right-0 z-20 bg-transparent backdrop-blur border-t border-gray-200/50 dark:border-gray-800/50">
            <div className="mx-auto w-full max-w-5xl px-4 sm:px-10 pt-0 pb-0">
              <div className="bg-transparent">
                <br />
                <ChatInput
                  onSubmit={addMessage}
                  disabled={query ? query.isLoading : false}
                  session_id={sessionId}
                />
              </div>
              <p className="text-[11px] text-center text-gray-500 dark:text-gray-400 mt-0.5 mb-0">
                This AI Assistant may make mistakes.{" "}
                <span className="underline cursor-pointer">
                  Check Important Info
                </span>
              </p>
            </div>
          </div>

          {/* Back-to-bottom button */}
          {showScrollButton && (
            <button
              onClick={scrollToBottom}
              aria-label="Scroll to bottom"
              className="fixed bottom-24 right-6 z-30 bg-blue-600 hover:bg-blue-700 text-white p-3 rounded-full shadow-lg transition-all duration-200"
            >
              <svg
                xmlns="http://www.w3.org/2000/svg"
                fill="none"
                viewBox="0 0 24 24"
                strokeWidth={2}
                stroke="currentColor"
                className="w-5 h-5"
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  d="M19 9l-7 7-7-7"
                />
              </svg>
            </button>
          )}
        </>
      )}
    </div>
  );
};

export default ChatWindow;
