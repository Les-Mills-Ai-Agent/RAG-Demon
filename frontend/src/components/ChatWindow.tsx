import React, { useEffect, useRef, useState } from "react";
import ChatBubble from "./ChatBubble";
import { AiMessage, Message, RAGRequest } from "../models/models";
import { v4 as uuid } from "uuid";
import { useBedrock } from "../hooks/useBedrock";
import { UseQueryResult } from "@tanstack/react-query";
import { ErrorResponse, RAGResponse, UserMessage } from "../models/models";
import { getChatCompletion } from "../utils/openai";
import ChatInput from "./ChatInput";
import { useLangchain } from "../hooks/useLangchain";
import { OmitKeyof } from "@tanstack/react-query";

// interface ChatWindowProps {
//   messages: Message[];
//   onRetry: (id: string) => void;
// }

type BackendImpl = "bedrock" | "langchain";

const ChatWindow = () => {
  const bottomRef = useRef<HTMLDivElement | null>(null);
  const [messages, setMessages] = useState<Message[]>([]);
  const [backendImpl, setBackendImpl] = useState<BackendImpl>("bedrock");
  const [retry, setRetry] = useState<boolean>(false);

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
    setMessages((ms) => {
      // Prevent duplicates
      if (ms.some((m) => m.message_id === message.message_id)) return ms;
      return [...ms, message];
    });
  };

  // useBedrock runs automatically when lastUserMessage changes
  const bedrockQuery = useBedrock(lastUserMessage);
  const langchainQuery = useLangchain();

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
      addMessage(aiMessage);
    }
  }, [query.data, query.isSuccess]);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  return (
    <div className="flex flex-col gap-4 w-full h-full">
      <div className="flex-1 overflow-y-auto flex flex-col gap-4">
        {messages.map((message) => {
          return (
            <ChatBubble
              key={message.message_id}
              msg={message}
              isLoading={false}
              error={null}
            />
          );
        })}
        {(query.isLoading || query.error) && (
          <ChatBubble
            msg={placeholderMessage}
            isLoading={query.isLoading}
            error={query.error}
          />
        )}
        <div ref={bottomRef} />
      </div>
      <ChatInput onSubmit={addMessage} disabled={query.isLoading} />
    </div>
  );
};

export default ChatWindow;
