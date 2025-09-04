import { useQuery } from "@tanstack/react-query";
import { ErrorResponse, RAGResponse, UserMessage } from "../models/models";
import { getBedrockResponse } from "../services/bedrockRagService";

export function useBedrock(message?: UserMessage) {
  // Ensure role is removed
  const request = message && {
    message_id: message.message_id,
    content: message.content,
    session_id: message.session_id,
    created_at: message.created_at,
  };

  return useQuery<RAGResponse, ErrorResponse>({
    queryKey: ["bedrock", request?.message_id],
    queryFn: () => getBedrockResponse(request!),
    enabled: !!request,
    staleTime: 5 * 60 * 1000,
    retry: 1,
  });
}
