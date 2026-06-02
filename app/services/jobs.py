import hashlib
import json
from datetime import UTC, datetime
from uuid import uuid4

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.domain.job_state import JobStatus
from app.models import Job


class IdempotencyConflictError(Exception):
    pass


def _payload_hash(payload: dict) -> str:
    canonical = json.dumps(payload, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(canonical.encode("utf-8")).hexdigest()


def create_job(
    session: Session,
    *,
    job_type: str,
    idempotency_key: str,
    payload: dict,
    priority: int = 100,
) -> Job:
    payload_hash = _payload_hash(payload)
    existing = session.scalar(select(Job).where(Job.idempotency_key == idempotency_key))
    if existing is not None:
        if existing.payload_hash != payload_hash:
            raise IdempotencyConflictError("same idempotency key used with different payload")
        return existing

    now = datetime.now(UTC)
    job = Job(
        type=job_type,
        status=JobStatus.QUEUED.value,
        payload=payload,
        payload_hash=payload_hash,
        idempotency_key=idempotency_key,
        priority=priority,
        attempt_count=0,
        max_attempts=3,
        next_run_at=now,
        trace_id=uuid4().hex,
        created_at=now,
        updated_at=now,
    )
    session.add(job)
    session.commit()
    session.refresh(job)
    return job


def get_job(session: Session, job_id: str) -> Job | None:
    return session.get(Job, job_id)
