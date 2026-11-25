import logging
import json
from collections.abc import AsyncGenerator

from app.infrastructure.llm_client import OllamaClient
from app.infrastructure.knowledge_base import KnowledgeBase
from app.domain.session import Session

logger = logging.getLogger(__name__)

SYSTEM_PROMPT = (
    "Ты — менеджер контакт-центра компании по банкротству физических лиц. "
    "Ты общаешься с потенциальным клиентом. Твоя ГЛАВНАЯ цель — записать подходящего "
    "клиента на бесплатную консультацию к юристу.\n\n"
    "АЛГОРИТМ ДИАЛОГА (следуй этим шагам по порядку):\n\n"
    "Шаг 1. ПРИВЕТСТВИЕ И ВЫЯВЛЕНИЕ СИТУАЦИИ\n"
    "— Выслушай клиента, пойми суть проблемы. Если тревожится — успокой.\n"
    "— Задай 1-2 уточняющих вопроса о ситуации (какие долги, перед кем).\n\n"
    "Шаг 2. КВАЛИФИКАЦИЯ КЛИЕНТА (обязательно выясни ДО записи)\n"
    "— Сумма долга: спроси общую сумму всех долгов. Берём в работу только от 350 000 руб.\n"
    "  Если меньше 350к — вежливо объясни, что для такой суммы процедура может быть "
    "нецелесообразна, предложи внесудебное банкротство через МФЦ.\n"
    "— Регион прописки: спроси регион. НЕ работаем в Чеченской республике, ДНР, ЛНР, "
    "Владимирской области. Если клиент из этих регионов — вежливо сообщи, что пока "
    "не работаем в его регионе.\n\n"
    "Шаг 3. ПРОДАЖА КОНСУЛЬТАЦИИ\n"
    "— Если клиент подходит (сумма от 350к, регион подходит) — переходи к записи.\n"
    "— Объясни: консультация бесплатная, ни к чему не обязывает. Юрист разберёт ситуацию, "
    "посчитает стоимость, объяснит риски и варианты.\n"
    "— Используй факты о компании к месту: опыт с 2017 года, 2500+ процедур, "
    "1,05 млрд списанных долгов, работа в 63 регионах.\n\n"
    "Шаг 4. ЗАПИСЬ НА КОНСУЛЬТАЦИЮ (главная цель!)\n"
    "— Спроси имя клиента.\n"
    "— Спроси номер телефона для связи.\n"
    "— Спроси удобное время для звонка юриста (день и время).\n"
    "— Подтверди запись: повтори имя, телефон, время. Скажи, что юрист позвонит "
    "в назначенное время.\n"
    "— Убедись, что клиент действительно готов ждать консультации.\n\n"
    "ВАЖНЫЕ ПРАВИЛА:\n"
    "— Говори спокойно, по-человечески, без юридического жаргона. Обращайся на «вы».\n"
    "— Отвечай на русском, 2-5 предложений. В конце задай вопрос или предложи шаг.\n"
    "— НЕ задавай вопросы, которые уже обсуждались в диалоге. Помни контекст беседы.\n"
    "— НЕ здоровайся повторно. НЕ переспрашивай то, что клиент уже сказал.\n"
    "— Двигай диалог ВПЕРЁД к записи. Не застревай на одном шаге.\n"
    "— Если вопрос не по теме — вежливо верни к теме банкротства.\n"
    "— Если клиент прямо просит записаться — сразу переходи к Шагу 4, "
    "но сначала уточни сумму и регион, если ещё не знаешь.\n\n"
)

FALLBACK_PROMPT = (
    "Ты — менеджер компании по банкротству. Ответь клиенту на русском, кратко и по-человечески. "
    "Если не знаешь точного ответа — предложи записаться на бесплатную консультацию к юристу. "
    "Вопрос клиента: "
)

CTX_LIMIT = 8192
TOKENS_PER_CHAR = 0.4


class AssistantService:
    def __init__(self, llm: OllamaClient, kb: KnowledgeBase) -> None:
        self._llm = llm
        self._kb = kb

    def _estimate(self, question: str, extra_tokens: int = 0) -> dict:
        q_tokens = int(len(question) * TOKENS_PER_CHAR)
        system_tokens = int(len(SYSTEM_PROMPT) * TOKENS_PER_CHAR)

        budget_for_context = CTX_LIMIT - system_tokens - q_tokens - extra_tokens - 400
        budget_for_context = max(budget_for_context, 500)

        top_k = 3 if budget_for_context > 1500 else 2
        context = self._kb.search(question, top_k=top_k)
        ctx_tokens = int(len(context) * TOKENS_PER_CHAR)

        if ctx_tokens > budget_for_context:
            char_limit = int(budget_for_context / TOKENS_PER_CHAR)
            context = context[:char_limit]
            ctx_tokens = int(len(context) * TOKENS_PER_CHAR)

        input_tokens = system_tokens + ctx_tokens + q_tokens + extra_tokens
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

    async def ask_stream(self, question: str, session: Session) -> AsyncGenerator[str, None]:
        logs: list[str] = []

        session.add_message("user", question)
        facts_summary, recent = session.get_llm_context()

        yield self._event("log", "Поиск в базе знаний...")

        history_tokens = int(
            sum(len(m["content"]) for m in recent[:-1]) * TOKENS_PER_CHAR
        )
        if facts_summary:
            history_tokens += int(len(facts_summary) * TOKENS_PER_CHAR)

        logs.append(f"Вопрос: {question[:100]}")
        logs.append(f"Сессия: {len(session.messages)} сообщ, отправляем {len(recent)} последних")
        if facts_summary:
            logs.append(f"Факты: {facts_summary}")

        plan = self._estimate(question, extra_tokens=history_tokens)
        logs.append(f"KB: top_k={plan['top_k']}, контекст {len(plan['context'])} симв")
        logs.append(f"Бюджет: ~{plan['input_tokens']} input tok, {plan['num_predict']} max output tok")
        logs.append(f"Сложность: {plan['complexity']}")

        yield self._event("log", f"Контекст: {len(plan['context'])} симв")
        yield self._event("estimate", json.dumps({
            "seconds": plan["est_seconds"],
            "complexity": plan["complexity"],
        }, ensure_ascii=False))
        yield self._event("log", "Генерация ответа...")

        system = SYSTEM_PROMPT
        if facts_summary:
            system += f"СОБРАННАЯ ИНФОРМАЦИЯ О КЛИЕНТЕ: {facts_summary}\n\n"
        system += f"Информация о компании и процедурах из регламента:\n{plan['context']}"

        history_for_llm = recent[:-1] if len(recent) > 1 else None

        answer, llm_logs = await self._llm.chat(
            system, question, num_predict=plan["num_predict"], history=history_for_llm,
        )
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
                "Я пока не смог подобрать точный ответ на ваш вопрос. "
                "Давайте я запишу вас на бесплатную консультацию к юристу — "
                "он разберёт вашу ситуацию детально. Хотите записаться?"
            )
            logs.append("Результат: все попытки пусты, fallback с предложением консультации")
        else:
            answer = self._trim_incomplete(answer)
            logs.append(f"Результат: {len(answer)} симв")

        session.add_message("assistant", answer)
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
