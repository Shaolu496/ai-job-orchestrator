from sqlalchemy import select

from app.models import Document, DocumentChunk, LlmUsage
from app.providers.embeddings import FakeEmbeddingProvider
from app.services.ingestion import ingest_document
from app.services.jobs import create_job


def test_ingest_document_creates_document_chunks_and_usage(db_session):
    job = create_job(
        db_session,
        job_type="document_ingestion",
        idempotency_key="document:a:v1",
        payload={"sourceName": "a.md", "content": "one two three four"},
    )

    ingest_document(db_session, job=job, embedding_provider=FakeEmbeddingProvider())

    document = db_session.scalar(select(Document))
    chunks = db_session.scalars(select(DocumentChunk).order_by(DocumentChunk.chunk_index)).all()
    usage = db_session.scalar(select(LlmUsage))

    assert document.source_name == "a.md"
    assert [chunk.content for chunk in chunks] == ["one two three four"]
    assert chunks[0].embedding_model == "fake-embedding-v1"
    assert usage.operation == "embedding"
    assert usage.input_tokens == 4
