from enum import StrEnum


class JobStatus(StrEnum):
    QUEUED = "queued"
    RUNNING = "running"
    RETRYING = "retrying"
    FAILED = "failed"
    COMPLETED = "completed"
    DEAD_LETTERED = "dead_lettered"


ALLOWED_TRANSITIONS: dict[JobStatus, set[JobStatus]] = {
    JobStatus.QUEUED: {JobStatus.RUNNING},
    JobStatus.RUNNING: {JobStatus.COMPLETED, JobStatus.RETRYING, JobStatus.FAILED},
    JobStatus.RETRYING: {JobStatus.QUEUED, JobStatus.DEAD_LETTERED},
    JobStatus.FAILED: set(),
    JobStatus.COMPLETED: set(),
    JobStatus.DEAD_LETTERED: set(),
}


def can_transition(current: JobStatus, target: JobStatus) -> bool:
    return target in ALLOWED_TRANSITIONS[current]
