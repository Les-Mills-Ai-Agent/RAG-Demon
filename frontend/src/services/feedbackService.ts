import api from "../utils/api";

/**
 * Sends a DynamoDB-ready feedback JSON document to your backend.
 * If your API requires auth, pass an id_token for the Authorization header.
 */
export async function sendFeedback(item: any, token?: string) {
  try {
    const res = await api.post("/feedback", item, {
      headers: {
        "Content-Type": "application/json",
        ...(token ? { Authorization: token } : {}), // add token if provided
      },
    });
    return res.data;
  } catch (error: any) {
    console.error("❌ Feedback submission failed:", error.response?.data || error.message);
    throw error;
  }
}
