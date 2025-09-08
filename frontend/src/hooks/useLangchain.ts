import { useQuery } from "@tanstack/react-query";
import { ErrorResponse, RAGResponse, UserMessage } from "../models/models";
import { getBedrockResponse } from "../services/bedrockRagService";

export function useLangchain(message?: UserMessage) {
  return useQuery<RAGResponse, ErrorResponse>({
    queryKey: ["bedrock", message],
    queryFn: () => getBedrockResponse(message!),
    enabled: !!message,
    staleTime: 5 * 60 * 1000,
    retry: 1,
  });
}
