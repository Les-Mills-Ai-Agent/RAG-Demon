import api from "../utils/api";

/**
 * Sends a DynamoDB-ready feedback JSON document to your backend.
 * Expects the caller to pass the full Authorization header value
 * (e.g., "Bearer <id_token>").
 */
export async function sendFeedback(item: any, token: string) {
  if (!token) throw new Error("Missing authorization token for feedback submission.");

  try {
    const res = await api.post("/feedback", item, {
      headers: {
        "Content-Type": "application/json",
        Authorization: token, // already prefixed in FeedbackProvider
      },
    });
    return res.data;
  } catch (error: any) {
    console.error("Feedback submission failed:", error.response?.data || error.message);
    throw error;
  }
}
