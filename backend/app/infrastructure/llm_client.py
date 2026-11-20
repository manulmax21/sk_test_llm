import re

import httpx

_THINK_RE = re.compile(r"<think>.*?</think>", re.DOTALL)


class OllamaClient:
    def __init__(self, base_url: str, model: str) -> None:
        self._base_url = base_url
        self._model = model

    async def chat(self, system: str, user: str) -> str:
        async with httpx.AsyncClient(timeout=300.0) as client:
            try:
                resp = await client.post(
                    f"{self._base_url}/api/chat",
                    json={
                        "model": self._model,
                        "messages": [
                            {"role": "system", "content": system},
                            {"role": "user", "content": user},
                        ],
                        "stream": False,
                        "options": {
                            "num_predict": 300,
                            "num_ctx": 4096,
                            "temperature": 0.3,
                        },
                    },
                )
                resp.raise_for_status()
                raw = resp.json()["message"]["content"]
                return _THINK_RE.sub("", raw).strip()
            except httpx.ConnectError as e:
                raise ConnectionError(f"Ollama недоступен: {e}") from e
