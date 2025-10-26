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
    select: (data) => removeDuplicateRefs(data),
    enabled: !!request,
    staleTime: Infinity,
    retry: 1,
    refetchOnWindowFocus: false,
    refetchOnReconnect: false,
    refetchOnMount: false,
  });
}

function removeDuplicateRefs(message: RAGResponse): RAGResponse {
  message.response_parts.forEach((part) => {
    const seen = new Set<string>();
    const uniqueRefs: { text: string; url: string }[] = [];

    part.references.forEach((r) => {
      if (!seen.has(r.url)) {
        seen.add(r.url);
        uniqueRefs.push(r);
      }
    });

    part.references = uniqueRefs;
  });

  return message;
}
