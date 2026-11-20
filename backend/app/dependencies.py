from functools import lru_cache

from app.config import Settings
from app.domain.assistant import AssistantService
from app.infrastructure.knowledge_base import KnowledgeBase
from app.infrastructure.llm_client import OllamaClient


@lru_cache
def get_settings() -> Settings:
    return Settings()


def get_assistant() -> AssistantService:
    s = get_settings()
    kb = KnowledgeBase(s.knowledge_base_path)
    llm = OllamaClient(s.ollama_url, s.model_name)
    return AssistantService(llm, kb)
