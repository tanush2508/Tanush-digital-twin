const BASE_URL = import.meta.env.VITE_API_BASE_URL || "http://127.0.0.1:8000";

export async function getStatus() {
  const res = await fetch(`${BASE_URL}/status`);
  if (!res.ok) {
    throw new Error(`Status request failed: ${res.status}`);
  }
  return res.json();
}

export async function sendMessage(message, debug = true) {
  const res = await fetch(`${BASE_URL}/chat`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({
      message,
      debug,
    }),
  });

  if (!res.ok) {
    const text = await res.text();
    throw new Error(text || `Chat request failed: ${res.status}`);
  }

  return res.json();
}