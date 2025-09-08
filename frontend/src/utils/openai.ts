// utils/openai.js
import axios, { AxiosError } from "axios";
import { Message } from "../models/models";

const SESSION_KEY = "lm-session-id";

// keep a stable session_id across page reloads
function getSessionId() {
  let id = localStorage.getItem(SESSION_KEY);
  if (!id) {
    id = crypto?.randomUUID?.() ?? Math.random().toString(36).slice(2);
    localStorage.setItem(SESSION_KEY, id);
  }
  return id;
}

/**
 * messages: array of { role: 'user'|'assistant'|'system', content: string }
 * We send just the LAST message because the backend uses only the last one.
 */
export async function getChatCompletion(message: Message) {
  try {
    const res = await axios.post("/api/chat", message, {
      headers: { "Content-Type": "application/json" },
    });
    return res.data.reply;
  } catch (err) {
    if (err instanceof AxiosError) {
      const detail = err?.response?.data?.detail;
      console.error("API Error:", err?.response || err);
      throw new Error(
        detail || "Failed to fetch assistant reply. Please try again."
      );
    }
  }
}
