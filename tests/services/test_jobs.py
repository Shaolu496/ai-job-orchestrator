import pytest

from app.services.jobs import IdempotencyConflictError, create_job


def test_create_job_returns_existing_job_for_same_key_and_same_payload(db_session):
    first = create_job(
        db_session,
        job_type="document_ingestion",
        idempotency_key="document:a:v1",
        payload={"sourceName": "a.md", "content": "hello"},
    )

    second = create_job(
        db_session,
        job_type="document_ingestion",
        idempotency_key="document:a:v1",
        payload={"sourceName": "a.md", "content": "hello"},
    )

    assert second.id == first.id


def test_create_job_rejects_same_key_with_different_payload(db_session):
    create_job(
        db_session,
        job_type="document_ingestion",
        idempotency_key="document:a:v1",
        payload={"sourceName": "a.md", "content": "hello"},
    )

    with pytest.raises(IdempotencyConflictError):
        create_job(
            db_session,
            job_type="document_ingestion",
            idempotency_key="document:a:v1",
            payload={"sourceName": "a.md", "content": "changed"},
        )
