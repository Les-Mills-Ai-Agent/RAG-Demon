import React, { useEffect, useRef, useState } from "react";
import ChatBubble from "./ChatBubble";
import { AiMessage, Message } from "../models/models";
import { useBedrock } from "../hooks/useBedrock";
import { useLangchain } from "../hooks/useLangchain";
import ChatInput from "./ChatInput";
import { UserMessage } from "../models/models";

type BackendImpl = "bedrock" | "langchain";

// accept a prop from App to pick the backend
type ChatWindowProps = {
  backendImpl?: BackendImpl; // optional; defaults to "bedrock"
  messages?: any[];
  readOnly?: boolean;
};

const ChatWindow = ({
  backendImpl: backendProp = "bedrock",
  messages: externalMessages,
  readOnly = false,
}: ChatWindowProps) => {
  const bottomRef = useRef<HTMLDivElement | null>(null);
  const [sessionId, setSessionId] = useState<string>();
  const [messages, setMessages] = useState<Message[]>(externalMessages || []);

  // Removed local mirrored state; just read the prop
  const backendImpl = backendProp;

  useEffect(() => {
    if (externalMessages) {
      setMessages(externalMessages);
    }
  }, [externalMessages]);

  const lastUserMessage = messages
    .slice()
    .reverse()
    .find((m) => m.role === "user");


  const placeholderMessage: AiMessage = {
    message_id: "",
    content: "",
    response_parts: [],
    session_id: "",
    created_at: "",
    role: "ai",
  };

  const addMessage = (message: Message) => {
    if (readOnly) return;

    setMessages((messages) => {
      // prevent duplicates
      if (messages.some((m) => m.message_id === message.message_id))
        return messages;
      return [...messages, message];
    });
  };

  const langchainQuery = useLangchain(readOnly ? undefined : lastUserMessage);
  const bedrockQuery = useBedrock(readOnly ? undefined : lastUserMessage);

  const query = backendImpl === "bedrock" ? bedrockQuery : langchainQuery;

  useEffect(() => {
    if (query.isSuccess && query.data && (!readOnly)) {
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
  }, [query.data, query.isSuccess, readOnly]);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  // Helper: find the nearest previous user message text before index `idx`
  const lastUserBefore = (idx: number): string => {
    for (let i = idx - 1; i >= 0; i--) {
      const m = messages[i];
      if (m && m.role === "user") return m.content ?? "";
    }
    return "";
  };

  return (
    <div className="flex flex-col gap-4 w-full h-full">
      <div className="flex-1 overflow-y-auto flex flex-col gap-4">
        {messages.map((message, idx) => (
          <ChatBubble
            key={message.message_id}
            msg={message}
            isLoading={false}
            error={null}
            // ➕ pass lastUserText only for AI bubbles (for the feedback modal)
            lastUserText={message.role === "ai" ? lastUserBefore(idx) : undefined}
          />
        ))}
        {(query.isLoading || query.error) && (
          <ChatBubble
            msg={placeholderMessage}
            isLoading={query.isLoading}
            error={query.error}
            onRetry={query.refetch}
          />
        )}
        <div ref={bottomRef} />
      </div>
      <ChatInput
        onSubmit={addMessage}
        disabled={query.isLoading}
        session_id={sessionId}
      />
    </div>
  );
};

export default ChatWindow;
