import { AxiosError } from "axios";
import axios from "axios";
import { ErrorResponse } from "../models/models";

export interface Conversation {
  session_id: string;
  user_id: string;
  created_at: string;
  last_updated: string;
}

export interface Message {
  message_id: string;
  content: string;
  session_id: string;
  created_at: string;
  response_parts?: any[];
}

const api = axios.create({
  baseURL: "https://gc6p3xa5c7.execute-api.us-east-1.amazonaws.com/Prod",
  headers: {
    "Content-Type": "application/json",
  },
  timeout: Infinity,
});

api.interceptors.response.use(
  (res) => res,
  (err: AxiosError<ErrorResponse>) => {
    const status = err.response?.data?.status ?? 500;
    const error = err.response?.data?.error ?? "UNKNOWN_ERROR";
    const message = err.response?.data?.message ?? err.message;

    return Promise.reject({
      status,
      error,
      message,
    } as ErrorResponse);
  }
);

export async function getConversations(userId: string): Promise<Conversation[]> {
  const res = await api.get<Conversation[]>(`/rag/bedrock/conversation/${userId}`);
  return res.data;
}

export async function getMessages(sessionId: string): Promise<Message[]> {
  const res = await api.get<Message[]>(`/rag/bedrock/messages/${sessionId}`);
  return res.data;
}

export default api;
