import { useQuery } from "@tanstack/react-query";
import type { ErrorResponse, RAGResponse, UserMessage, Message } from "../models/models";
import { getLangchainResponse } from "../services/langchainRagService";

export function useLangchain(
  message?: UserMessage | Message,
  opts?: { enabled?: boolean }
) {
  const enabled = !!message && (opts?.enabled ?? true);

  return useQuery<RAGResponse, ErrorResponse>({
    queryKey: ["langchain", message?.message_id],
    enabled,
    queryFn: () => getLangchainResponse(message as UserMessage),
    staleTime: 5 * 60 * 1000,
    retry: 1,
  });
}
