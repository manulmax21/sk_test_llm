const API_URL = import.meta.env.VITE_API_URL || "";

export async function sendQuestion(question) {
  const resp = await fetch(`${API_URL}/api/chat`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ question }),
  });

  if (!resp.ok) {
    const err = await resp.json().catch(() => ({}));
    throw new Error(err.detail || `Ошибка ${resp.status}`);
  }

  const data = await resp.json();
  return data.answer;
}
