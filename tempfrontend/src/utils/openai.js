// utils/openai.js
import axios from 'axios';

const SESSION_KEY = 'lm-session-id';

// keep a stable session_id across page reloads
function getSessionId() {
  let id = localStorage.getItem(SESSION_KEY);
  if (!id) {
    id = (crypto?.randomUUID?.() ?? Math.random().toString(36).slice(2));
    localStorage.setItem(SESSION_KEY, id);
  }
  return id;
}

/**
 * messages: array of { role: 'user'|'assistant'|'system', content: string }
 * We send just the LAST message because the backend uses only the last one.
 */
export async function getChatCompletion(messages) {
  const last = messages[messages.length - 1] || { role: 'user', content: '' };

  const payload = {
    session_id: getSessionId(),
    messages: [{ role: last.role || 'user', content: String(last.content) }],
  };

  try {
    const res = await axios.post('/api/chat', payload, {
      headers: { 'Content-Type': 'application/json' },
    });
    return res.data.reply;
  } catch (err) {
    const detail = err?.response?.data?.detail;
    console.error('API Error:', err?.response || err);
    throw new Error(detail || 'Failed to fetch assistant reply. Please try again.');
  }
}
