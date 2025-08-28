from typing import Protocol, Dict, Any

class LLMClient(Protocol):
    def generate(self, *, prompt: str, **kwargs: Any) -> str:
        ...

class EmbeddingsClient(Protocol):
    def embed(self, *, texts: list[str]) -> list[list[float]]:
        ...

    