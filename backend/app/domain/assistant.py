from app.infrastructure.llm_client import OllamaClient
from app.infrastructure.knowledge_base import KnowledgeBase

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

    async def ask(self, question: str) -> str:
        context = self._kb.search(question, top_k=5)
        system = f"{SYSTEM_PROMPT}\n\nКонтекст:\n{context}"
        return await self._llm.chat(system, question)
