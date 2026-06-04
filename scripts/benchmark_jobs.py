import logging
import os
import sys
import time
from pathlib import Path
from uuid import uuid4

from fastapi.testclient import TestClient

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

os.environ.setdefault(
    "DATABASE_URL",
    "postgresql+psycopg://postgres:postgres@localhost:55432/ai_jobs",
)

from app.database import Base, engine  # noqa: E402
from app.main import create_app  # noqa: E402


def main() -> None:
    logging.getLogger("httpx").setLevel(logging.WARNING)
    Base.metadata.drop_all(engine)
    Base.metadata.create_all(engine)

    client = TestClient(create_app())
    jobs = int(os.getenv("BENCHMARK_JOBS", "100"))
    run_id = uuid4().hex[:8]
    failures = 0
    started = time.perf_counter()

    for index in range(jobs):
        response = client.post(
            "/jobs",
            json={
                "type": "document_ingestion",
                "idempotencyKey": f"benchmark:{run_id}:{index}",
                "payload": {
                    "sourceName": f"doc-{index}.md",
                    "content": "latency retry timeout budget observability",
                },
            },
        )
        if response.status_code not in {200, 201}:
            failures += 1

    elapsed = time.perf_counter() - started
    print(
        {
            "mode": "fastapi_testclient",
            "jobs": jobs,
            "failures": failures,
            "elapsed_seconds": round(elapsed, 3),
            "jobs_per_second": round(jobs / elapsed, 2),
        }
    )


if __name__ == "__main__":
    main()
