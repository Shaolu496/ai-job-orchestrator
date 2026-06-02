from app.workers.tasks import execute_job_once


def test_retrieval_query_returns_matching_chunks(client, db_session, fake_embedding_provider):
    create_response = client.post(
        "/jobs",
        json={
            "type": "document_ingestion",
            "idempotencyKey": "document:retrieval:v1",
            "payload": {"sourceName": "risk.md", "content": "latency budget retry timeout"},
        },
    )
    job_id = create_response.json()["id"]

    execute_job_once(db_session, job_id, embedding_provider=fake_embedding_provider)

    response = client.post("/retrieval/query", json={"query": "retry timeout", "topK": 3})

    assert response.status_code == 200
    body = response.json()
    assert body["results"][0]["content"] == "latency budget retry timeout"
    assert body["results"][0]["score"] >= 0
