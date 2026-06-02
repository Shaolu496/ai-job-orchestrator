from typing import Any, Literal

from pydantic import BaseModel, Field


class CreateJobRequest(BaseModel):
    type: Literal["document_ingestion"]
    idempotency_key: str = Field(alias="idempotencyKey", min_length=8, max_length=255)
    payload: dict[str, Any]
    priority: int = 100


class JobResponse(BaseModel):
    id: str
    type: str
    status: str
    trace_id: str
    attempt_count: int
    max_attempts: int


class RetrievalRequest(BaseModel):
    query: str
    top_k: int = Field(default=5, alias="topK", ge=1, le=20)
