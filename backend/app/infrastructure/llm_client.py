import httpx


class OllamaClient:
    def __init__(self, base_url: str, model: str) -> None:
        self._base_url = base_url
        self._model = model

    async def generate(self, prompt: str) -> str:
        async with httpx.AsyncClient(timeout=120.0) as client:
            try:
                resp = await client.post(
                    f"{self._base_url}/api/generate",
                    json={
                        "model": self._model,
                        "prompt": prompt,
                        "stream": False,
                    },
                )
                resp.raise_for_status()
                return resp.json()["response"]
            except httpx.ConnectError as e:
                raise ConnectionError(f"Ollama недоступен: {e}") from e
