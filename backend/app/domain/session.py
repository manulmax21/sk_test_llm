import time
import re
from dataclasses import dataclass, field

MAX_SESSIONS = 500
SESSION_TTL = 3600
RECENT_MESSAGES = 6


@dataclass
class ClientFacts:
    debt_amount: str = ""
    region: str = ""
    name: str = ""
    phone: str = ""
    preferred_time: str = ""
    situation: str = ""

    def summary(self) -> str:
        parts = []
        if self.situation:
            parts.append(f"Ситуация: {self.situation}")
        if self.debt_amount:
            parts.append(f"Сумма долга: {self.debt_amount}")
        if self.region:
            parts.append(f"Регион: {self.region}")
        if self.name:
            parts.append(f"Имя: {self.name}")
        if self.phone:
            parts.append(f"Телефон: {self.phone}")
        if self.preferred_time:
            parts.append(f"Удобное время: {self.preferred_time}")
        return "; ".join(parts) if parts else ""


@dataclass
class Session:
    messages: list[dict] = field(default_factory=list)
    facts: ClientFacts = field(default_factory=ClientFacts)
    created_at: float = field(default_factory=time.time)
    last_active: float = field(default_factory=time.time)

    def add_message(self, role: str, content: str) -> None:
        self.messages.append({"role": role, "content": content})
        self.last_active = time.time()
        if role == "user":
            self._extract_facts(content)

    def get_llm_context(self) -> tuple[str, list[dict]]:
        """Return (facts_summary, recent_messages) for LLM."""
        summary = self.facts.summary()
        recent = self.messages[-RECENT_MESSAGES:]
        return summary, recent

    def _extract_facts(self, text: str) -> None:
        lower = text.lower()

        money = re.findall(
            r'(\d[\d\s.,]*)\s*(?:тыс|тысяч|руб|₽|млн|миллион|р\b)',
            lower,
        )
        if money and not self.facts.debt_amount:
            self.facts.debt_amount = money[0].strip()

        phone = re.findall(
            r'(?:\+7|8)[\s\-()]*\d{3}[\s\-()]*\d{3}[\s\-]*\d{2}[\s\-]*\d{2}',
            text,
        )
        if phone:
            self.facts.phone = phone[0].strip()

        regions = [
            "москв", "петербург", "новосибирск", "екатеринбург", "казан",
            "краснодар", "самар", "ростов", "уфа", "воронеж", "волгоград",
            "пермь", "тюмен", "омск", "челябинск", "красноярск",
        ]
        oblast_pattern = re.findall(
            r'(?:из|в|прописан[аы]?\s+в)\s+([а-яё]+(?:\s+(?:области?|крае?|республик[еи]))?)',
            lower,
        )
        if oblast_pattern and not self.facts.region:
            self.facts.region = oblast_pattern[0].strip()
        elif not self.facts.region:
            for r in regions:
                if r in lower:
                    self.facts.region = r
                    break


class SessionStore:
    def __init__(self) -> None:
        self._sessions: dict[str, Session] = {}

    def get_or_create(self, session_id: str) -> Session:
        self._cleanup()
        if session_id not in self._sessions:
            self._sessions[session_id] = Session()
        return self._sessions[session_id]

    def _cleanup(self) -> None:
        if len(self._sessions) <= MAX_SESSIONS:
            return
        now = time.time()
        expired = [
            sid for sid, s in self._sessions.items()
            if now - s.last_active > SESSION_TTL
        ]
        for sid in expired:
            del self._sessions[sid]
        if len(self._sessions) > MAX_SESSIONS:
            oldest = sorted(self._sessions, key=lambda k: self._sessions[k].last_active)
            for sid in oldest[: len(oldest) - MAX_SESSIONS]:
                del self._sessions[sid]
