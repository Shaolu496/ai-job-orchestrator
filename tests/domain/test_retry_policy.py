from app.domain.retry_policy import next_retry_delay_seconds


def test_retry_delay_uses_exponential_backoff():
    assert next_retry_delay_seconds(attempt_count=1) == 2
    assert next_retry_delay_seconds(attempt_count=2) == 4
    assert next_retry_delay_seconds(attempt_count=3) == 8


def test_retry_delay_is_capped():
    assert next_retry_delay_seconds(attempt_count=20) == 300
