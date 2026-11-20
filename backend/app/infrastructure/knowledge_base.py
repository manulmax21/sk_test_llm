import re
from pathlib import Path


class KnowledgeBase:
    def __init__(self, path: str) -> None:
        full_text = Path(path).read_text(encoding="utf-8")
        self._chunks = self._split(full_text)

    def get_text(self) -> str:
        return "\n\n".join(self._chunks)

    def search(self, query: str, top_k: int = 5) -> str:
        query_words = set(self._tokenize(query))
        scored = []
        for chunk in self._chunks:
            chunk_words = set(self._tokenize(chunk))
            overlap = len(query_words & chunk_words)
            if overlap > 0:
                scored.append((overlap, chunk))
        scored.sort(key=lambda x: x[0], reverse=True)
        results = [chunk for _, chunk in scored[:top_k]]
        if not results:
            results = self._chunks[:3]
        return "\n\n".join(results)

    @staticmethod
    def _split(text: str) -> list[str]:
        chunks = []
        current = []
        for line in text.split("\n"):
            stripped = line.strip()
            if not stripped and current:
                chunk = "\n".join(current).strip()
                if len(chunk) > 50:
                    chunks.append(chunk)
                current = []
            else:
                current.append(line)
        if current:
            chunk = "\n".join(current).strip()
            if len(chunk) > 50:
                chunks.append(chunk)
        if not chunks:
            for i in range(0, len(text), 1000):
                chunks.append(text[i:i + 1000])
        return chunks

    @staticmethod
    def _tokenize(text: str) -> list[str]:
        return [w.lower() for w in re.findall(r"[а-яёa-z]{3,}", text.lower())]
