import { useQuery } from "@tanstack/react-query";
import { ErrorResponse, RAGResponse, UserMessage } from "../models/models";
import { getBedrockResponse } from "../services/bedrockRagService";
import { useAuth } from "react-oidc-context";

export function useBedrock(message?: UserMessage) {
  const auth = useAuth();
  const request = message && {
    message_id: message.message_id,
    content: message.content,
    session_id: message.session_id,
    created_at: message.created_at,
  };

  return useQuery<RAGResponse, ErrorResponse>({
    queryKey: ["bedrock", request?.message_id],
    queryFn: () => getBedrockResponse(request!, auth.user?.id_token!),
    enabled: !!request,
    staleTime: 5 * 60 * 1000,
    retry: 1,
  });
}
