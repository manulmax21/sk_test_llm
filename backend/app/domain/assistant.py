from app.infrastructure.llm_client import OllamaClient
from app.infrastructure.knowledge_base import KnowledgeBase

SYSTEM_PROMPT = (
    "Ты — ассистент контакт-центра компании по банкротству физических лиц. "
    "Отвечай на вопросы ТОЛЬКО на основе регламента ниже. "
    "Если в регламенте нет информации для ответа, скажи об этом. "
    "Отвечай на русском языке, кратко и по делу.\n\n"
    "=== РЕГЛАМЕНТ ===\n{context}\n=== КОНЕЦ РЕГЛАМЕНТА ==="
)


class AssistantService:
    def __init__(self, llm: OllamaClient, kb: KnowledgeBase) -> None:
        self._llm = llm
        self._kb = kb

    async def ask(self, question: str) -> str:
        system = SYSTEM_PROMPT.format(context=self._kb.get_text())
        return await self._llm.chat(system, question)
