const API_URL = import.meta.env.VITE_API_URL || "";

export async function sendQuestionStream(question, onStatus) {
  const resp = await fetch(`${API_URL}/api/chat`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ question }),
  });

  if (!resp.ok) {
    const err = await resp.json().catch(() => ({}));
    throw new Error(err.detail || `Ошибка ${resp.status}`);
  }

  const reader = resp.body.getReader();
  const decoder = new TextDecoder();
  let buffer = "";
  let result = { answer: "", logs: [] };

  while (true) {
    const { done, value } = await reader.read();
    if (done) break;

    buffer += decoder.decode(value, { stream: true });
    const lines = buffer.split("\n");
    buffer = lines.pop() || "";

    for (const line of lines) {
      if (!line.startsWith("data: ")) continue;
      try {
        const event = JSON.parse(line.slice(6));

        if (event.type === "log" && onStatus) {
          onStatus(event.message);
        }

        if (event.type === "done") {
          result = { answer: event.message, logs: event.logs || [] };
        }

        if (event.type === "error") {
          throw new Error(event.message);
        }
      } catch (e) {
        if (e instanceof SyntaxError) continue;
        throw e;
      }
    }
  }

  return result;
}
