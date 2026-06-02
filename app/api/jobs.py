from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_session
from app.schemas import CreateJobRequest, JobResponse
from app.services.jobs import IdempotencyConflictError, create_job, get_job

router = APIRouter(prefix="/jobs", tags=["jobs"])
SessionDep = Annotated[Session, Depends(get_session)]


@router.post("", response_model=JobResponse, status_code=status.HTTP_201_CREATED)
def post_job(request: CreateJobRequest, session: SessionDep) -> JobResponse:
    try:
        job = create_job(
            session,
            job_type=request.type,
            idempotency_key=request.idempotency_key,
            payload=request.payload,
            priority=request.priority,
        )
    except IdempotencyConflictError as exc:
        raise HTTPException(status_code=409, detail=str(exc)) from exc
    return JobResponse(
        id=job.id,
        type=job.type,
        status=job.status,
        trace_id=job.trace_id,
        attempt_count=job.attempt_count,
        max_attempts=job.max_attempts,
    )


@router.get("/{job_id}", response_model=JobResponse)
def get_job_by_id(job_id: str, session: SessionDep) -> JobResponse:
    job = get_job(session, job_id)
    if job is None:
        raise HTTPException(status_code=404, detail="job not found")
    return JobResponse(
        id=job.id,
        type=job.type,
        status=job.status,
        trace_id=job.trace_id,
        attempt_count=job.attempt_count,
        max_attempts=job.max_attempts,
    )
