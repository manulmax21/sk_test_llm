from pathlib import Path


class KnowledgeBase:
    def __init__(self, path: str) -> None:
        self._text = Path(path).read_text(encoding="utf-8")

    def get_text(self) -> str:
        return self._text
