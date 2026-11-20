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

    async def chat(self, system: str, user: str) -> tuple[str, list[str]]:
        logs: list[str] = []
        logs.append(f"LLM: модель {self._model}, URL {self._base_url}")
        logs.append(f"LLM: system prompt {len(system)} символов, вопрос {len(user)} символов")
        logger.info("Запрос к Ollama: model=%s, system_len=%d, user_len=%d", self._model, len(system), len(user))

        start = time.time()
        async with httpx.AsyncClient(timeout=None) as client:
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
                elapsed = round(time.time() - start, 1)
                logs.append(f"LLM: HTTP {resp.status_code}, время {elapsed} сек")
                logger.info("Ответ Ollama: status=%d, elapsed=%.1fs", resp.status_code, elapsed)

                resp.raise_for_status()
                data = resp.json()

                raw = data.get("message", {}).get("content", "")
                logs.append(f"LLM: raw ответ {len(raw)} символов")

                if data.get("eval_count"):
                    tokens = data["eval_count"]
                    tps = round(tokens / elapsed, 1) if elapsed > 0 else 0
                    logs.append(f"LLM: {tokens} токенов, {tps} tok/s")

                answer = _THINK_RE.sub("", raw).strip()
                if not answer:
                    logs.append("LLM: ответ пуст после очистки thinking-тегов")
                    logger.warning("Пустой ответ после очистки: raw_len=%d", len(raw))

                return answer, logs

            except httpx.ConnectError as e:
                logs.append(f"LLM: ошибка подключения — {e}")
                logger.error("ConnectError: %s", e)
                raise ConnectionError(f"Ollama недоступен: {e}") from e
            except httpx.HTTPStatusError as e:
                elapsed = round(time.time() - start, 1)
                body = e.response.text[:300]
                logs.append(f"LLM: HTTP ошибка {e.response.status_code} за {elapsed} сек — {body}")
                logger.error("HTTP %d: %s", e.response.status_code, body)
                raise
