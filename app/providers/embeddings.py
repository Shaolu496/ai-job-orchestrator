import hashlib
from typing import Protocol


class EmbeddingProvider(Protocol):
    model: str
    provider: str

    def embed(self, text: str) -> list[float]:
        pass


class FakeEmbeddingProvider:
    model = "fake-embedding-v1"
    provider = "fake"

    def embed(self, text: str) -> list[float]:
        digest = hashlib.sha256(text.encode("utf-8")).digest()
        return [round(digest[index] / 255, 6) for index in range(8)]


class FailingEmbeddingProvider:
    model = "failing-embedding-v1"
    provider = "fake"

    def embed(self, text: str) -> list[float]:
        raise TimeoutError("embedding provider timeout")
