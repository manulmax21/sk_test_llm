import re
from pathlib import Path


class KnowledgeBase:
    def __init__(self, path: str) -> None:
        full_text = Path(path).read_text(encoding="utf-8")
        self._chunks = self._split(full_text)

    def get_text(self) -> str:
        return "\n\n".join(self._chunks)

    def search(self, query: str, top_k: int = 3) -> str:
        query_words = set(self._tokenize(query))
        scored = []
        for chunk in self._chunks:
            chunk_words = set(self._tokenize(chunk))
            if not chunk_words:
                continue
            overlap = len(query_words & chunk_words)
            score = overlap / max(len(query_words), 1)
            if score > 0:
                scored.append((score, chunk))
        scored.sort(key=lambda x: x[0], reverse=True)
        results = [chunk for _, chunk in scored[:top_k]]
        if not results:
            results = self._chunks[:2]
        return "\n\n".join(results)

    @staticmethod
    def _split(text: str) -> list[str]:
        lines = text.split("\n")
        chunks = []
        for line in lines:
            stripped = line.strip()
            if len(stripped) > 80:
                chunks.append(stripped)
            elif stripped and chunks:
                chunks[-1] += " " + stripped
        return [c for c in chunks if len(c) > 50]

    @staticmethod
    def _tokenize(text: str) -> list[str]:
        return [w.lower() for w in re.findall(r"[а-яёa-z]{3,}", text.lower())]
