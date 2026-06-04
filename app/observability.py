import logging
from contextvars import ContextVar

_DEFAULT_TRACE_ID = "-"
_FACTORY_INSTALLED = False
_TRACE_ID: ContextVar[str] = ContextVar("trace_id", default=_DEFAULT_TRACE_ID)


def _install_trace_id_factory() -> None:
    global _FACTORY_INSTALLED
    if _FACTORY_INSTALLED:
        return

    previous_factory = logging.getLogRecordFactory()

    def record_factory(*args: object, **kwargs: object) -> logging.LogRecord:
        record = previous_factory(*args, **kwargs)
        record.trace_id = _TRACE_ID.get()
        return record

    logging.setLogRecordFactory(record_factory)
    _FACTORY_INSTALLED = True


def configure_logging() -> None:
    _install_trace_id_factory()
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s trace_id=%(trace_id)s %(message)s",
    )


def log_event(logger: logging.Logger, *, trace_id: str, event: str, **fields: object) -> None:
    details = " ".join(f"{key}={value}" for key, value in sorted(fields.items()))
    token = _TRACE_ID.set(trace_id)
    try:
        logger.info("%s %s", event, details)
    finally:
        _TRACE_ID.reset(token)
