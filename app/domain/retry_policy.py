def next_retry_delay_seconds(*, attempt_count: int, cap_seconds: int = 300) -> int:
    delay = 2**attempt_count
    return min(delay, cap_seconds)
