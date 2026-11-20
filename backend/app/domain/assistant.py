import logging
import json
from collections.abc import AsyncGenerator

from app.infrastructure.llm_client import OllamaClient
from app.infrastructure.knowledge_base import KnowledgeBase

logger = logging.getLogger(__name__)

SYSTEM_PROMPT = (
    "Ты — ассистент контакт-центра компании по банкротству физических лиц.\n"
    "Правила:\n"
    "1. Отвечай ТОЛЬКО на вопросы про банкротство, долги, юриспруденцию и работу компании.\n"
    "2. Если вопрос не по теме — ответь: «Пожалуйста, задайте вопрос по теме банкротства или юриспруденции.»\n"
    "3. Используй ТОЛЬКО информацию из контекста ниже.\n"
    "4. Отвечай на русском, кратко — 2-4 предложения."
)


class AssistantService:
    def __init__(self, llm: OllamaClient, kb: KnowledgeBase) -> None:
        self._llm = llm
        self._kb = kb

    async def ask(self, question: str) -> tuple[str, list[str]]:
        logs: list[str] = []

        logs.append(f"Вопрос: {question[:100]}")
        context = self._kb.search(question, top_k=5)
        logs.append(f"KB: найдено контекста {len(context)} символов")
        logger.info("KB search: question=%s, context_len=%d", question[:50], len(context))

        system = f"{SYSTEM_PROMPT}\n\nКонтекст:\n{context}"
        logs.append("LLM: отправка запроса...")

        answer, llm_logs = await self._llm.chat(system, question)
        logs.extend(llm_logs)

        if not answer:
            answer = "Модель не вернула ответ. Попробуйте переформулировать вопрос."
            logs.append("Результат: пустой ответ, подставлен fallback")
        else:
            logs.append(f"Результат: ответ {len(answer)} символов")

        return answer, logs

    async def ask_stream(self, question: str) -> AsyncGenerator[str, None]:
        logs: list[str] = []

        yield self._event("log", "Поиск в базе знаний...")

        logs.append(f"Вопрос: {question[:100]}")
        context = self._kb.search(question, top_k=5)
        logs.append(f"KB: найдено контекста {len(context)} символов")

        yield self._event("log", f"Найдено {len(context)} символов контекста")
        yield self._event("log", "Отправка запроса в LLM...")

        system = f"{SYSTEM_PROMPT}\n\nКонтекст:\n{context}"
        answer, llm_logs = await self._llm.chat(system, question)
        logs.extend(llm_logs)

        if not answer:
            answer = "Модель не вернула ответ. Попробуйте переформулировать вопрос."
            logs.append("Результат: пустой ответ, подставлен fallback")
        else:
            logs.append(f"Результат: ответ {len(answer)} символов")

        yield self._event("done", answer, logs)

    @staticmethod
    def _event(etype: str, message: str, logs: list[str] | None = None) -> str:
        data: dict = {"type": etype, "message": message}
        if logs is not None:
            data["logs"] = logs
        return f"data: {json.dumps(data, ensure_ascii=False)}\n\n"
