from app.domain.job_state import JobStatus
from app.services.jobs import create_job, get_job
from app.workers.tasks import execute_job_once


def test_worker_marks_successful_job_completed(db_session, fake_embedding_provider):
    job = create_job(
        db_session,
        job_type="document_ingestion",
        idempotency_key="document:worker-success:v1",
        payload={"sourceName": "a.md", "content": "hello world"},
    )

    execute_job_once(db_session, job.id, embedding_provider=fake_embedding_provider)

    updated = get_job(db_session, job.id)
    assert updated.status == JobStatus.COMPLETED.value


def test_worker_moves_job_to_dead_letter_after_max_attempts(db_session, failing_embedding_provider):
    job = create_job(
        db_session,
        job_type="document_ingestion",
        idempotency_key="document:worker-fail:v1",
        payload={"sourceName": "a.md", "content": "hello world"},
    )
    job.max_attempts = 1
    db_session.commit()

    execute_job_once(db_session, job.id, embedding_provider=failing_embedding_provider)

    updated = get_job(db_session, job.id)
    assert updated.status == JobStatus.DEAD_LETTERED.value
