import hashlib
from datetime import UTC, datetime

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.domain.chunking import chunk_text
from app.models import Document, DocumentChunk, Job, JobStep, LlmUsage
from app.providers.embeddings import EmbeddingProvider


def _content_hash(content: str) -> str:
    return hashlib.sha256(content.encode("utf-8")).hexdigest()


def ingest_document(session: Session, *, job: Job, embedding_provider: EmbeddingProvider) -> None:
    payload = job.payload
    source_name = str(payload["sourceName"])
    content = str(payload["content"])
    content_hash = _content_hash(content)
    now = datetime.now(UTC)

    document = session.scalar(select(Document).where(Document.content_hash == content_hash))
    if document is None:
        document = Document(
            source_name=source_name,
            content_hash=content_hash,
            metadata_={"source": source_name},
            created_at=now,
        )
        session.add(document)
        session.flush()

    chunks = chunk_text(content)
    input_tokens = 0
    for index, chunk in enumerate(chunks):
        token_count = len(chunk.split())
        input_tokens += token_count
        session.add(
            DocumentChunk(
                document_id=document.id,
                chunk_index=index,
                content=chunk,
                embedding=embedding_provider.embed(chunk),
                embedding_model=embedding_provider.model,
                token_count=token_count,
                metadata_={"traceId": job.trace_id},
            )
        )

    session.add(
        JobStep(
            job_id=job.id,
            name="document_ingestion",
            status="completed",
            input={"sourceName": source_name},
            output={"documentId": document.id, "chunkCount": len(chunks)},
            started_at=now,
            finished_at=datetime.now(UTC),
        )
    )
    session.add(
        LlmUsage(
            job_id=job.id,
            provider=embedding_provider.provider,
            model=embedding_provider.model,
            operation="embedding",
            input_tokens=input_tokens,
            output_tokens=0,
            estimated_cost=0,
            created_at=datetime.now(UTC),
        )
    )
    session.commit()
