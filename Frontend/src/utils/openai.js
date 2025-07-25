import axios from 'axios'

export async function getChatCompletion(messages) {
  try {
    const res = await axios.post('/api/chat', { messages })
    return res.data.reply
  } catch (err) {
    console.error('API Error:', err?.response || err.message)

    //friendly error to avoid leaking stack traces or internal info
    throw new Error(
      err?.response?.data?.detail || 'Failed to fetch assistant reply. Please try again.'
    )
  }
}
