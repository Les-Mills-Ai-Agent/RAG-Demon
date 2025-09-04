import { ComponentState } from "react";
import type { paths, components } from "../../schema.d.ts";
import { v4 as uuid } from "uuid";

export type RAGRequest = components["schemas"]["RAGRequest"];
export type RAGResponse = components["schemas"]["RAGResponse"];
export type Chunk = components["schemas"]["Chunk"];
export type ResponsePart = components["schemas"]["ResponsePart"];
export type ErrorResponse = components["schemas"]["ErrorResponse"];
export type ConversationMetadata = components["schemas"]["Conversation"];

// Utility to "flatten" intersections
type Simplify<T> = { [K in keyof T]: T[K] } & {};

export type UserMessage = Simplify<RAGRequest & { role: "user" }>;
export type AiMessage = Simplify<RAGResponse & { role: "ai" }>;

export type Message = UserMessage | AiMessage;

export function newUserMessage(query: string): UserMessage {
  return {
    message_id: uuid(),
    content: query,
    session_id: undefined,
    created_at: new Date().toISOString(),
    role: "user",
  };
}
