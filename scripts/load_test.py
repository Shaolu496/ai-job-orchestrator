import argparse
import time

import httpx


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--base-url", default="http://127.0.0.1:8000")
    parser.add_argument("--jobs", type=int, default=100)
    args = parser.parse_args()

    started = time.perf_counter()
    failures = 0

    with httpx.Client(timeout=10) as client:
        for index in range(args.jobs):
            response = client.post(
                f"{args.base_url}/jobs",
                json={
                    "type": "document_ingestion",
                    "idempotencyKey": f"load-test:{index}",
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
            "jobs": args.jobs,
            "failures": failures,
            "elapsed_seconds": round(elapsed, 3),
            "jobs_per_second": round(args.jobs / elapsed, 2),
        }
    )


if __name__ == "__main__":
    main()
