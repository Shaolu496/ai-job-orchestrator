from datetime import UTC, datetime, timedelta

from sqlalchemy.orm import Session

from app.database import SessionLocal
from app.domain.job_state import JobStatus
from app.domain.retry_policy import next_retry_delay_seconds
from app.models import Job
from app.providers.embeddings import EmbeddingProvider, FakeEmbeddingProvider
from app.services.ingestion import ingest_document
from app.workers.celery_app import celery_app


def execute_job_once(
    session: Session,
    job_id: str,
    *,
    embedding_provider: EmbeddingProvider | None = None,
) -> None:
    provider = embedding_provider or FakeEmbeddingProvider()
    job = session.get(Job, job_id)
    if job is None or job.status not in {JobStatus.QUEUED.value, JobStatus.RETRYING.value}:
        return

    now = datetime.now(UTC)
    job.status = JobStatus.RUNNING.value
    job.attempt_count += 1
    job.updated_at = now
    session.commit()

    try:
        if job.type == "document_ingestion":
            ingest_document(session, job=job, embedding_provider=provider)
        job.status = JobStatus.COMPLETED.value
        job.updated_at = datetime.now(UTC)
        session.commit()
    except Exception:
        if job.attempt_count >= job.max_attempts:
            job.status = JobStatus.DEAD_LETTERED.value
        else:
            delay = next_retry_delay_seconds(attempt_count=job.attempt_count)
            job.status = JobStatus.RETRYING.value
            job.next_run_at = datetime.now(UTC) + timedelta(seconds=delay)
        job.updated_at = datetime.now(UTC)
        session.commit()


@celery_app.task(name="execute_job")
def execute_job(job_id: str) -> None:
    with SessionLocal() as session:
        execute_job_once(session, job_id)
