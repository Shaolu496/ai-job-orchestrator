import logging


def configure_logging() -> None:
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s trace_id=%(trace_id)s %(message)s",
    )


def log_event(logger: logging.Logger, *, trace_id: str, event: str, **fields: object) -> None:
    details = " ".join(f"{key}={value}" for key, value in sorted(fields.items()))
    logger.info("%s %s", event, details, extra={"trace_id": trace_id})
