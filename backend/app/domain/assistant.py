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

FALLBACK_PROMPT = (
    "Ты — ассистент контакт-центра компании по банкротству физических лиц. "
    "Ответь кратко на русском, 1-2 предложения. Вопрос: "
)

CTX_LIMIT = 4096
TOKENS_PER_CHAR = 0.4


class AssistantService:
    def __init__(self, llm: OllamaClient, kb: KnowledgeBase) -> None:
        self._llm = llm
        self._kb = kb

    def _estimate(self, question: str) -> dict:
        q_tokens = int(len(question) * TOKENS_PER_CHAR)
        system_tokens = int(len(SYSTEM_PROMPT) * TOKENS_PER_CHAR)

        budget_for_context = CTX_LIMIT - system_tokens - q_tokens - 400
        budget_for_context = max(budget_for_context, 500)

        top_k = 3 if budget_for_context > 1500 else 2
        context = self._kb.search(question, top_k=top_k)
        ctx_tokens = int(len(context) * TOKENS_PER_CHAR)

        if ctx_tokens > budget_for_context:
            char_limit = int(budget_for_context / TOKENS_PER_CHAR)
            context = context[:char_limit]
            ctx_tokens = int(len(context) * TOKENS_PER_CHAR)

        input_tokens = system_tokens + ctx_tokens + q_tokens
        num_predict = min(CTX_LIMIT - input_tokens, 800)
        num_predict = max(num_predict, 200)

        total_tokens = input_tokens + num_predict
        if total_tokens < 1500:
            complexity = "easy"
        elif total_tokens < 2800:
            complexity = "medium"
        else:
            complexity = "hard"

        tps = 3.0
        est_seconds = int(input_tokens / 50 + num_predict / tps)

        return {
            "context": context,
            "num_predict": num_predict,
            "input_tokens": input_tokens,
            "est_seconds": est_seconds,
            "complexity": complexity,
            "top_k": top_k,
        }

    async def ask_stream(self, question: str) -> AsyncGenerator[str, None]:
        logs: list[str] = []

        yield self._event("log", "Поиск в базе знаний...")

        logs.append(f"Вопрос: {question[:100]}")
        plan = self._estimate(question)
        logs.append(f"KB: top_k={plan['top_k']}, контекст {len(plan['context'])} симв")
        logs.append(f"Бюджет: ~{plan['input_tokens']} input tok, {plan['num_predict']} max output tok")
        logs.append(f"Сложность: {plan['complexity']}")

        yield self._event("log", f"Контекст: {len(plan['context'])} симв")
        yield self._event("estimate", json.dumps({
            "seconds": plan["est_seconds"],
            "complexity": plan["complexity"],
        }, ensure_ascii=False))
        yield self._event("log", "Генерация ответа...")

        system = f"{SYSTEM_PROMPT}\n\nКонтекст:\n{plan['context']}"
        answer, llm_logs = await self._llm.chat(system, question, num_predict=plan["num_predict"])
        logs.extend(llm_logs)

        if not answer:
            logs.append("Попытка 2: упрощённый запрос без контекста")
            yield self._event("log", "Повторный запрос...")
            answer, retry_logs = await self._llm.chat(
                FALLBACK_PROMPT + question, question, num_predict=300,
            )
            logs.extend(retry_logs)

        if not answer:
            logs.append("Попытка 3: минимальный запрос")
            answer, retry_logs = await self._llm.chat(
                "Ответь кратко на русском.", question, num_predict=200,
            )
            logs.extend(retry_logs)

        if not answer:
            answer = (
                "К сожалению, не удалось сформировать ответ на ваш вопрос. "
                "Пожалуйста, попробуйте переформулировать или задать более короткий вопрос."
            )
            logs.append("Результат: все попытки пусты, fallback-текст")
        else:
            answer = self._trim_incomplete(answer)
            logs.append(f"Результат: {len(answer)} симв")

        yield self._event("done", answer, logs)

    @staticmethod
    def _trim_incomplete(text: str) -> str:
        if text.endswith((".", "!", "?", "»", ";")):
            return text
        last = max(text.rfind("."), text.rfind("!"), text.rfind("?"))
        if last > len(text) // 3:
            return text[: last + 1]
        return text

    @staticmethod
    def _event(etype: str, message: str, logs: list[str] | None = None) -> str:
        data: dict = {"type": etype, "message": message}
        if logs is not None:
            data["logs"] = logs
        return f"data: {json.dumps(data, ensure_ascii=False)}\n\n"
