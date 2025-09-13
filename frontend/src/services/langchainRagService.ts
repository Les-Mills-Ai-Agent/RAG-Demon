// frontend/src/services/langchainRagService.ts
import axios, { AxiosError } from "axios";
import { v4 as uuid } from "uuid";
import type { RAGResponse, UserMessage } from "../models/models";


//Calls the LangChain RAG backend.
// If you don't have a Vite proxy for /api -> http://127.0.0.1:8000,
// replace "/api/chat" with "http://127.0.0.1:8000/api/chat".
 
export async function getLangchainResponse(message: UserMessage): Promise<RAGResponse> {
  try {
    const res = await axios.post<{ reply: string; session_id: string }>(
      "/api/chat",
      {
        session_id: message.session_id ?? null,
        messages: [
          // System priming should live server-side; we only send the user message
          { role: "user", content: message.content },
        ],
      },
      {
        headers: { "Content-Type": "application/json" },
        withCredentials: true, // mirrors fetch(..., { credentials: "include" })
      }
    );

    const data = res.data;

    // Adapt to app-wide RAGResponse shape
    const rag: RAGResponse = {
      message_id: uuid(),
      content: data.reply,
      response_parts: [], // populate if you later chunk the reply
      session_id: data.session_id,
      created_at: new Date().toISOString(),
    };

    return rag;
  } catch (err) {
    const e = err as AxiosError;
    const status = e.response?.status ?? 0;
    const details =
      typeof e.response?.data === "string"
        ? e.response?.data
        : JSON.stringify(e.response?.data ?? {}, null, 2);

    // keep throw shape similar to your previous code
    throw { message: `LangChain chat failed: ${status}`, details };
  }
}
