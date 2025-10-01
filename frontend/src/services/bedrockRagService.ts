import { RAGRequest, RAGResponse } from "../models/models";
import api from "../utils/api";

export async function getBedrockResponse(
  body: RAGRequest,
  token: string
): Promise<RAGResponse> {
  const response = await api.post("/rag/bedrock", body, {
    headers: {
      Authorization: token,
    },
    timeout: Infinity,
  });
  return response.data;
}
