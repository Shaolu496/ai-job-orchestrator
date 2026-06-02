def test_create_job_api_returns_201(client):
    response = client.post(
        "/jobs",
        json={
            "type": "document_ingestion",
            "idempotencyKey": "document:a:v1",
            "payload": {"sourceName": "a.md", "content": "hello"},
        },
    )

    assert response.status_code == 201
    body = response.json()
    assert body["type"] == "document_ingestion"
    assert body["status"] == "queued"
    assert body["trace_id"]


def test_create_job_api_returns_409_for_idempotency_conflict(client):
    payload = {
        "type": "document_ingestion",
        "idempotencyKey": "document:a:v1",
        "payload": {"sourceName": "a.md", "content": "hello"},
    }
    assert client.post("/jobs", json=payload).status_code == 201

    payload["payload"]["content"] = "changed"
    response = client.post("/jobs", json=payload)

    assert response.status_code == 409
