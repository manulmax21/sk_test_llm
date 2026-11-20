import re
import time
import logging

import httpx

logger = logging.getLogger(__name__)

_THINK_RE = re.compile(r"<think>.*?</think>", re.DOTALL)


class OllamaClient:
    def __init__(self, base_url: str, model: str) -> None:
        self._base_url = base_url
        self._model = model

    async def chat(self, system: str, user: str, num_predict: int = 500) -> tuple[str, list[str]]:
        logs: list[str] = []
        logs.append(f"LLM: модель {self._model}, num_predict={num_predict}")
        logs.append(f"LLM: system {len(system)} симв, вопрос {len(user)} симв")

        start = time.time()
        async with httpx.AsyncClient(timeout=None) as client:
            try:
                resp = await client.post(
                    f"{self._base_url}/api/chat",
                    json={
                        "model": self._model,
                        "messages": [
                            {"role": "system", "content": system},
                            {"role": "user", "content": "/no_think " + user},
                        ],
                        "stream": False,
                        "options": {
                            "num_predict": num_predict,
                            "num_ctx": CTX_LIMIT,
                            "temperature": 0.3,
                        },
                    },
                )
                elapsed = round(time.time() - start, 1)
                logs.append(f"LLM: HTTP {resp.status_code}, {elapsed} сек")
                logger.info("Ollama: status=%d, %.1fs", resp.status_code, elapsed)

                resp.raise_for_status()
                data = resp.json()

                raw = data.get("message", {}).get("content", "")
                logs.append(f"LLM: raw {len(raw)} симв")

                if data.get("eval_count"):
                    tokens = data["eval_count"]
                    tps = round(tokens / elapsed, 1) if elapsed > 0 else 0
                    hit_limit = tokens >= num_predict
                    logs.append(f"LLM: {tokens} tok, {tps} tok/s" + (" (лимит!)" if hit_limit else ""))

                answer = _THINK_RE.sub("", raw).strip()
                if not answer and raw:
                    logs.append("LLM: thinking съел ответ, возвращаю raw")
                    answer = raw.strip()

                return answer, logs

            except httpx.ConnectError as e:
                logs.append(f"LLM: ошибка — {e}")
                raise ConnectionError(f"Ollama недоступен: {e}") from e
            except httpx.HTTPStatusError as e:
                elapsed = round(time.time() - start, 1)
                body = e.response.text[:300]
                logs.append(f"LLM: HTTP {e.response.status_code}, {elapsed} сек — {body}")
                raise


CTX_LIMIT = 4096
