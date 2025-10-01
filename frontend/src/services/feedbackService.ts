import api from "../utils/api";

/**
 * Sends a DynamoDB-ready feedback JSON document to your backend.
 * If your API requires auth, pass an id_token for the Authorization header.
 */
export async function sendFeedback(item: any, token?: string) {
  const res = await api.post("/feedback", item, {
    headers: token ? { Authorization: token } : undefined,
  });
  return res.data;
}
