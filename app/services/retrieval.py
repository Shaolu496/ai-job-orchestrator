from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import DocumentChunk
from app.providers.embeddings import EmbeddingProvider


def _cosine_like_score(left: list[float], right: list[float]) -> float:
    return float(round(sum(a * b for a, b in zip(left, right, strict=True)), 6))


def query_chunks(
    session: Session,
    *,
    query: str,
    top_k: int,
    embedding_provider: EmbeddingProvider,
) -> list[dict]:
    query_embedding = embedding_provider.embed(query)
    chunks = session.scalars(select(DocumentChunk)).all()
    ranked = sorted(
        (
            {
                "documentId": chunk.document_id,
                "chunkId": chunk.id,
                "content": chunk.content,
                "score": _cosine_like_score(query_embedding, chunk.embedding),
            }
            for chunk in chunks
        ),
        key=lambda item: item["score"],
        reverse=True,
    )
    return ranked[:top_k]
