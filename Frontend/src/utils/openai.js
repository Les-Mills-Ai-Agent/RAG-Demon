import axios from 'axios'

export async function getChatCompletion(messages) {
  // Proxy via Vite to your Python backend
  const res = await axios.post('/api/chat', { messages })
  return res.data.reply
}
