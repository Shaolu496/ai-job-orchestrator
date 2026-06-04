import logging

from app.observability import configure_logging, log_event


def test_log_event_includes_trace_id_and_fields(caplog):
    logger = logging.getLogger("test_observability")

    with caplog.at_level(logging.INFO):
        log_event(
            logger,
            trace_id="trace-123",
            event="job_started",
            job_id="job-1",
            status="running",
        )

    record = caplog.records[0]
    assert record.trace_id == "trace-123"
    assert "job_started" in record.message
    assert "job_id=job-1" in record.message
    assert "status=running" in record.message


def test_configure_logging_adds_default_trace_id_to_plain_logs(caplog):
    logger = logging.getLogger("plain_logger")
    configure_logging()

    with caplog.at_level(logging.INFO):
        logger.info("plain message")

    assert caplog.records[0].trace_id == "-"
