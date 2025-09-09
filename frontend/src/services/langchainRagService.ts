import { RAGResponse, UserMessage } from "../models/models";
import { v4 as uuid } from "uuid";

export async function getLangchainResponse(message: UserMessage): Promise<RAGResponse> {
  // If you don't have a Vite proxy for /api -> 127.0.0.1:8000,
  // use the full URL: "http://127.0.0.1:8000/api/chat"
  const res = await fetch("/api/chat", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    credentials: "include",
    body: JSON.stringify({
      session_id: message.session_id ?? null,
      messages: [
        // if you want system priming, include it in server.py; here we just send the user msg
        { role: "user", content: message.content }
      ],
    }),
  });

  if (!res.ok) {
    const text = await res.text().catch(() => "");
    throw { message: `LangChain chat failed: ${res.status}`, details: text } as any;
  }

  // Server returns { reply, session_id }
  const data = await res.json() as { reply: string; session_id: string };

  // Adapt to your app-wide RAGResponse shape expected by ChatWindow
  return {
    message_id: uuid(),
    content: data.reply,
    response_parts: [],         // or split if you want parts
    session_id: data.session_id,
    created_at: new Date().toISOString(),
  };
}
