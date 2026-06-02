import pytest

from app.domain.job_state import JobStatus, can_transition


@pytest.mark.parametrize(
    ("current", "target"),
    [
        (JobStatus.QUEUED, JobStatus.RUNNING),
        (JobStatus.RUNNING, JobStatus.COMPLETED),
        (JobStatus.RUNNING, JobStatus.RETRYING),
        (JobStatus.RETRYING, JobStatus.QUEUED),
        (JobStatus.RETRYING, JobStatus.DEAD_LETTERED),
        (JobStatus.RUNNING, JobStatus.FAILED),
    ],
)
def test_allowed_transitions(current: JobStatus, target: JobStatus):
    assert can_transition(current, target) is True


@pytest.mark.parametrize(
    ("current", "target"),
    [
        (JobStatus.COMPLETED, JobStatus.RUNNING),
        (JobStatus.DEAD_LETTERED, JobStatus.QUEUED),
        (JobStatus.FAILED, JobStatus.RUNNING),
        (JobStatus.QUEUED, JobStatus.COMPLETED),
    ],
)
def test_disallowed_transitions(current: JobStatus, target: JobStatus):
    assert can_transition(current, target) is False
