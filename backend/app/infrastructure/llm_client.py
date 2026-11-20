import httpx


class OllamaClient:
    def __init__(self, base_url: str, model: str) -> None:
        self._base_url = base_url
        self._model = model

    async def chat(self, system: str, user: str) -> str:
        async with httpx.AsyncClient(timeout=120.0) as client:
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
                    },
                )
                resp.raise_for_status()
                return resp.json()["message"]["content"]
            except httpx.ConnectError as e:
                raise ConnectionError(f"Ollama недоступен: {e}") from e
