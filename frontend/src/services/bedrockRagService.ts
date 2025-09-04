import { RAGRequest, RAGResponse } from "../models/models";
import api from "../utils/api";

export async function getBedrockResponse(
  body: RAGRequest
): Promise<RAGResponse> {
  const response = await api.post("/rag/bedrock", body);
  return response.data;
}
