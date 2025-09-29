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
};

const ChatWindow = ({
  backendImpl: backendProp = "bedrock",
}: ChatWindowProps) => {
  const bottomRef = useRef<HTMLDivElement | null>(null);
  const [sessionId, setSessionId] = useState<string>();
  const [messages, setMessages] = useState<Message[]>([]);

  // Removed local mirrored state; just read the prop
  const backendImpl = backendProp;

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
    setMessages((messages) => {
      // prevent duplicates
      if (messages.some((m) => m.message_id === message.message_id))
        return messages;
      return [...messages, message];
    });
  };

  // call hooks with a single argument each (no options object)
  const langchainQuery = useLangchain(lastUserMessage);
  const bedrockQuery = useBedrock(lastUserMessage);
  // pick the active one
  const query = backendImpl === "bedrock" ? bedrockQuery : langchainQuery;

  useEffect(() => {
    if (query.isSuccess && query.data) {
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
  }, [query.data, query.isSuccess]);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  return (
    <div className="flex flex-col gap-4 w-full h-full">
      <div className="flex-1 overflow-y-auto flex flex-col gap-4">
        {messages.map((message) => (
          <ChatBubble
            key={message.message_id}
            msg={message}
            isLoading={false}
            error={null}
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
