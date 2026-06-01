# AI Job Orchestrator Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a FastAPI + Celery backend platform that executes long-running AI document ingestion jobs with idempotency, retry behavior, observability, retrieval, and test evidence suitable for FAANG-style senior SWE interviews.

**Architecture:** FastAPI owns request validation and job creation. Postgres is the source of truth for jobs, steps, documents, chunks, and usage records. Redis/Celery handles async dispatch, while workers execute deterministic job steps through a provider abstraction that can use fake embeddings in tests and real embeddings later.

**Tech Stack:** Python 3.12, FastAPI, SQLAlchemy 2, Alembic, Pydantic, Celery, Redis, Postgres + pgvector, pytest, ruff, Docker Compose.

---

## File Structure

- Create: `pyproject.toml`
  - Python package metadata, dependencies, pytest and ruff config.
- Create: `docker-compose.yml`
  - Local Postgres with pgvector and Redis.
- Create: `.env.example`
  - Local configuration contract.
- Create: `app/main.py`
  - FastAPI app factory and router registration.
- Create: `app/config.py`
  - Settings from environment variables.
- Create: `app/database.py`
  - SQLAlchemy engine, session factory, and dependency.
- Create: `app/models.py`
  - SQLAlchemy tables for jobs, job steps, documents, chunks, and LLM usage.
- Create: `app/schemas.py`
  - Pydantic request/response models.
- Create: `app/domain/job_state.py`
  - Job status enum and allowed state transitions.
- Create: `app/domain/retry_policy.py`
  - Exponential backoff with jitter cap.
- Create: `app/domain/chunking.py`
  - Deterministic text chunking.
- Create: `app/services/jobs.py`
  - Job creation, idempotency checks, state updates, and job reads.
- Create: `app/services/ingestion.py`
  - Document ingestion workflow.
- Create: `app/services/retrieval.py`
  - Query embedding and similarity lookup.
- Create: `app/providers/embeddings.py`
  - Embedding provider protocol plus deterministic fake provider.
- Create: `app/workers/celery_app.py`
  - Celery app configuration.
- Create: `app/workers/tasks.py`
  - Celery task entrypoint for job execution.
- Create: `app/api/jobs.py`
  - `POST /jobs` and `GET /jobs/{job_id}`.
- Create: `app/api/retrieval.py`
  - `POST /retrieval/query`.
- Create: `app/api/health.py`
  - `GET /health`.
- Create: `alembic.ini`
  - Alembic config.
- Create: `alembic/env.py`
  - Alembic metadata binding.
- Create: `alembic/versions/0001_initial_schema.py`
  - Initial schema and indexes.
- Create: `tests/conftest.py`
  - Test DB/session setup and dependency overrides.
- Create: `tests/domain/test_job_state.py`
- Create: `tests/domain/test_retry_policy.py`
- Create: `tests/domain/test_chunking.py`
- Create: `tests/services/test_jobs.py`
- Create: `tests/services/test_ingestion.py`
- Create: `tests/api/test_jobs_api.py`
- Create: `tests/api/test_retrieval_api.py`
- Modify: `readme.md`
  - Add startup commands, API examples, state machine, testing evidence, and FAANG discussion guide after implementation.

---

## Task 1: Project Skeleton And Health Endpoint

**FAANG evidence:** Shows a clean service boundary and repeatable local setup instead of a one-off script.

**Files:**
- Create: `pyproject.toml`
- Create: `.env.example`
- Create: `app/__init__.py`
- Create: `app/main.py`
- Create: `app/config.py`
- Create: `app/api/__init__.py`
- Create: `app/api/health.py`
- Create: `tests/conftest.py`
- Create: `tests/api/test_health_api.py`

- [ ] **Step 1: Write the failing health endpoint test**

Create `tests/api/test_health_api.py`:

```python
from fastapi.testclient import TestClient

from app.main import create_app


def test_health_returns_ok():
    client = TestClient(create_app())

    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok", "service": "ai-job-orchestrator"}
```

- [ ] **Step 2: Create package config**

Create `pyproject.toml`:

```toml
[project]
name = "ai-job-orchestrator"
version = "0.1.0"
requires-python = ">=3.12"
dependencies = [
  "alembic>=1.13.0",
  "celery>=5.4.0",
  "fastapi>=0.115.0",
  "httpx>=0.27.0",
  "pgvector>=0.3.0",
  "psycopg[binary]>=3.2.0",
  "pydantic-settings>=2.4.0",
  "redis>=5.0.0",
  "sqlalchemy>=2.0.0",
  "uvicorn[standard]>=0.30.0"
]

[project.optional-dependencies]
dev = [
  "pytest>=8.3.0",
  "pytest-cov>=5.0.0",
  "ruff>=0.6.0"
]

[tool.pytest.ini_options]
testpaths = ["tests"]
pythonpath = ["."]

[tool.ruff]
line-length = 100
target-version = "py312"

[tool.ruff.lint]
select = ["E", "F", "I", "UP", "B"]
```

- [ ] **Step 3: Create environment example**

Create `.env.example`:

```env
DATABASE_URL=postgresql+psycopg://postgres:postgres@localhost:5432/ai_jobs
REDIS_URL=redis://localhost:6379/0
SERVICE_NAME=ai-job-orchestrator
EMBEDDING_PROVIDER=fake
```

- [ ] **Step 4: Implement the health endpoint**

Create `app/__init__.py`:

```python
```

Create `app/config.py`:

```python
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    database_url: str = "sqlite+pysqlite:///:memory:"
    redis_url: str = "redis://localhost:6379/0"
    service_name: str = "ai-job-orchestrator"
    embedding_provider: str = "fake"

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")
```

Create `app/api/__init__.py`:

```python
```

Create `app/api/health.py`:

```python
from fastapi import APIRouter

from app.config import Settings

router = APIRouter()


@router.get("/health")
def health() -> dict[str, str]:
    settings = Settings()
    return {"status": "ok", "service": settings.service_name}
```

Create `app/main.py`:

```python
from fastapi import FastAPI

from app.api.health import router as health_router


def create_app() -> FastAPI:
    app = FastAPI(title="AI Job Orchestrator")
    app.include_router(health_router)
    return app


app = create_app()
```

- [ ] **Step 5: Run test to verify it passes**

Run:

```bash
python -m pytest tests/api/test_health_api.py -v
```

Expected: 1 passed.

- [ ] **Step 6: Run lint**

Run:

```bash
python -m ruff check .
```

Expected: All checks passed.

- [ ] **Step 7: Commit**

```bash
git add pyproject.toml .env.example app tests
git commit -m "建立 FastAPI 專案骨架"
```

---

## Task 2: Database Schema And Job State Machine

**FAANG evidence:** Shows explicit consistency model, state transition constraints, indexes, and data ownership.

**Files:**
- Create: `docker-compose.yml`
- Create: `app/database.py`
- Create: `app/models.py`
- Create: `app/domain/__init__.py`
- Create: `app/domain/job_state.py`
- Create: `alembic.ini`
- Create: `alembic/env.py`
- Create: `alembic/versions/0001_initial_schema.py`
- Create: `tests/domain/test_job_state.py`

- [ ] **Step 1: Write failing state machine tests**

Create `tests/domain/test_job_state.py`:

```python
import pytest

from app.domain.job_state import JobStatus, can_transition


@pytest.mark.parametrize(
    ("current", "target"),
    [
        (JobStatus.QUEUED, JobStatus.RUNNING),
        (JobStatus.RUNNING, JobStatus.COMPLETED),
        (JobStatus.RUNNING, JobStatus.RETRYING),
        (JobStatus.RETRYING, JobStatus.QUEUED),
        (JobStatus.RETRYING, JobStatus.DEAD_LETTERED),
        (JobStatus.RUNNING, JobStatus.FAILED),
    ],
)
def test_allowed_transitions(current: JobStatus, target: JobStatus):
    assert can_transition(current, target) is True


@pytest.mark.parametrize(
    ("current", "target"),
    [
        (JobStatus.COMPLETED, JobStatus.RUNNING),
        (JobStatus.DEAD_LETTERED, JobStatus.QUEUED),
        (JobStatus.FAILED, JobStatus.RUNNING),
        (JobStatus.QUEUED, JobStatus.COMPLETED),
    ],
)
def test_disallowed_transitions(current: JobStatus, target: JobStatus):
    assert can_transition(current, target) is False
```

- [ ] **Step 2: Implement job state domain**

Create `app/domain/__init__.py`:

```python
```

Create `app/domain/job_state.py`:

```python
from enum import StrEnum


class JobStatus(StrEnum):
    QUEUED = "queued"
    RUNNING = "running"
    RETRYING = "retrying"
    FAILED = "failed"
    COMPLETED = "completed"
    DEAD_LETTERED = "dead_lettered"


ALLOWED_TRANSITIONS: dict[JobStatus, set[JobStatus]] = {
    JobStatus.QUEUED: {JobStatus.RUNNING},
    JobStatus.RUNNING: {JobStatus.COMPLETED, JobStatus.RETRYING, JobStatus.FAILED},
    JobStatus.RETRYING: {JobStatus.QUEUED, JobStatus.DEAD_LETTERED},
    JobStatus.FAILED: set(),
    JobStatus.COMPLETED: set(),
    JobStatus.DEAD_LETTERED: set(),
}


def can_transition(current: JobStatus, target: JobStatus) -> bool:
    return target in ALLOWED_TRANSITIONS[current]
```

- [ ] **Step 3: Add Docker Compose**

Create `docker-compose.yml`:

```yaml
services:
  postgres:
    image: pgvector/pgvector:pg16
    environment:
      POSTGRES_DB: ai_jobs
      POSTGRES_USER: postgres
      POSTGRES_PASSWORD: postgres
    ports:
      - "5432:5432"
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U postgres -d ai_jobs"]
      interval: 5s
      timeout: 3s
      retries: 10

  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"
    healthcheck:
      test: ["CMD", "redis-cli", "ping"]
      interval: 5s
      timeout: 3s
      retries: 10
```

- [ ] **Step 4: Implement database and models**

Create `app/database.py`:

```python
from collections.abc import Generator

from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker

from app.config import Settings


class Base(DeclarativeBase):
    pass


settings = Settings()
engine = create_engine(settings.database_url, pool_pre_ping=True)
SessionLocal = sessionmaker(bind=engine, autoflush=False, expire_on_commit=False)


def get_session() -> Generator[Session, None, None]:
    with SessionLocal() as session:
        yield session
```

Create `app/models.py`:

```python
from datetime import datetime
from typing import Any
from uuid import uuid4

from pgvector.sqlalchemy import Vector
from sqlalchemy import DateTime, ForeignKey, Index, Integer, Numeric, String, Text, UniqueConstraint
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base
from app.domain.job_state import JobStatus


class Job(Base):
    __tablename__ = "jobs"
    __table_args__ = (
        UniqueConstraint("idempotency_key", name="uq_jobs_idempotency_key"),
        Index("ix_jobs_status_next_run_at", "status", "next_run_at"),
    )

    id: Mapped[str] = mapped_column(UUID(as_uuid=False), primary_key=True, default=lambda: str(uuid4()))
    type: Mapped[str] = mapped_column(String(64), nullable=False)
    status: Mapped[str] = mapped_column(String(32), nullable=False, default=JobStatus.QUEUED.value)
    payload: Mapped[dict[str, Any]] = mapped_column(JSONB, nullable=False)
    payload_hash: Mapped[str] = mapped_column(String(64), nullable=False)
    idempotency_key: Mapped[str] = mapped_column(String(255), nullable=False)
    priority: Mapped[int] = mapped_column(Integer, nullable=False, default=100)
    attempt_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    max_attempts: Mapped[int] = mapped_column(Integer, nullable=False, default=3)
    next_run_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    trace_id: Mapped[str] = mapped_column(String(64), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)

    steps: Mapped[list["JobStep"]] = relationship(back_populates="job", cascade="all, delete-orphan")


class JobStep(Base):
    __tablename__ = "job_steps"
    __table_args__ = (Index("ix_job_steps_job_id_name", "job_id", "name"),)

    id: Mapped[str] = mapped_column(UUID(as_uuid=False), primary_key=True, default=lambda: str(uuid4()))
    job_id: Mapped[str] = mapped_column(UUID(as_uuid=False), ForeignKey("jobs.id"), nullable=False)
    name: Mapped[str] = mapped_column(String(64), nullable=False)
    status: Mapped[str] = mapped_column(String(32), nullable=False)
    input: Mapped[dict[str, Any]] = mapped_column(JSONB, nullable=False, default=dict)
    output: Mapped[dict[str, Any]] = mapped_column(JSONB, nullable=False, default=dict)
    error_code: Mapped[str | None] = mapped_column(String(64))
    error_message: Mapped[str | None] = mapped_column(Text)
    started_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    finished_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))

    job: Mapped[Job] = relationship(back_populates="steps")


class Document(Base):
    __tablename__ = "documents"
    __table_args__ = (UniqueConstraint("content_hash", name="uq_documents_content_hash"),)

    id: Mapped[str] = mapped_column(UUID(as_uuid=False), primary_key=True, default=lambda: str(uuid4()))
    source_name: Mapped[str] = mapped_column(String(255), nullable=False)
    content_hash: Mapped[str] = mapped_column(String(64), nullable=False)
    metadata: Mapped[dict[str, Any]] = mapped_column(JSONB, nullable=False, default=dict)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)


class DocumentChunk(Base):
    __tablename__ = "document_chunks"
    __table_args__ = (Index("ix_document_chunks_document_id", "document_id"),)

    id: Mapped[str] = mapped_column(UUID(as_uuid=False), primary_key=True, default=lambda: str(uuid4()))
    document_id: Mapped[str] = mapped_column(UUID(as_uuid=False), ForeignKey("documents.id"), nullable=False)
    chunk_index: Mapped[int] = mapped_column(Integer, nullable=False)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    embedding: Mapped[list[float]] = mapped_column(Vector(8), nullable=False)
    embedding_model: Mapped[str] = mapped_column(String(128), nullable=False)
    token_count: Mapped[int] = mapped_column(Integer, nullable=False)
    metadata: Mapped[dict[str, Any]] = mapped_column(JSONB, nullable=False, default=dict)


class LlmUsage(Base):
    __tablename__ = "llm_usage"
    __table_args__ = (Index("ix_llm_usage_job_id", "job_id"),)

    id: Mapped[str] = mapped_column(UUID(as_uuid=False), primary_key=True, default=lambda: str(uuid4()))
    job_id: Mapped[str] = mapped_column(UUID(as_uuid=False), ForeignKey("jobs.id"), nullable=False)
    provider: Mapped[str] = mapped_column(String(64), nullable=False)
    model: Mapped[str] = mapped_column(String(128), nullable=False)
    operation: Mapped[str] = mapped_column(String(64), nullable=False)
    input_tokens: Mapped[int] = mapped_column(Integer, nullable=False)
    output_tokens: Mapped[int] = mapped_column(Integer, nullable=False)
    estimated_cost: Mapped[float] = mapped_column(Numeric(12, 6), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
```

- [ ] **Step 5: Add Alembic files**

Create `alembic.ini`:

```ini
[alembic]
script_location = alembic
prepend_sys_path = .

[loggers]
keys = root,sqlalchemy,alembic

[handlers]
keys = console

[formatters]
keys = generic

[logger_root]
level = WARN
handlers = console

[logger_sqlalchemy]
level = WARN
handlers =
qualname = sqlalchemy.engine

[logger_alembic]
level = INFO
handlers =
qualname = alembic

[handler_console]
class = StreamHandler
args = (sys.stderr,)
level = NOTSET
formatter = generic

[formatter_generic]
format = %(levelname)-5.5s [%(name)s] %(message)s
```

Create `alembic/env.py`:

```python
from logging.config import fileConfig

from alembic import context
from sqlalchemy import engine_from_config, pool

from app.config import Settings
from app.database import Base
from app import models

config = context.config
config.set_main_option("sqlalchemy.url", Settings().database_url)

if config.config_file_name is not None:
    fileConfig(config.config_file_name)

target_metadata = Base.metadata


def run_migrations_offline() -> None:
    context.configure(url=Settings().database_url, target_metadata=target_metadata, literal_binds=True)
    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    connectable = engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )
    with connectable.connect() as connection:
        context.configure(connection=connection, target_metadata=target_metadata)
        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
```

Create `alembic/versions/0001_initial_schema.py`:

```python
import pgvector.sqlalchemy
import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision = "0001_initial_schema"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute("CREATE EXTENSION IF NOT EXISTS vector")
    op.create_table(
        "jobs",
        sa.Column("id", postgresql.UUID(as_uuid=False), primary_key=True),
        sa.Column("type", sa.String(length=64), nullable=False),
        sa.Column("status", sa.String(length=32), nullable=False),
        sa.Column("payload", postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column("payload_hash", sa.String(length=64), nullable=False),
        sa.Column("idempotency_key", sa.String(length=255), nullable=False),
        sa.Column("priority", sa.Integer(), nullable=False),
        sa.Column("attempt_count", sa.Integer(), nullable=False),
        sa.Column("max_attempts", sa.Integer(), nullable=False),
        sa.Column("next_run_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("trace_id", sa.String(length=64), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.UniqueConstraint("idempotency_key", name="uq_jobs_idempotency_key"),
    )
    op.create_index("ix_jobs_status_next_run_at", "jobs", ["status", "next_run_at"])
    op.create_table(
        "documents",
        sa.Column("id", postgresql.UUID(as_uuid=False), primary_key=True),
        sa.Column("source_name", sa.String(length=255), nullable=False),
        sa.Column("content_hash", sa.String(length=64), nullable=False),
        sa.Column("metadata", postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.UniqueConstraint("content_hash", name="uq_documents_content_hash"),
    )
    op.create_table(
        "job_steps",
        sa.Column("id", postgresql.UUID(as_uuid=False), primary_key=True),
        sa.Column("job_id", postgresql.UUID(as_uuid=False), sa.ForeignKey("jobs.id"), nullable=False),
        sa.Column("name", sa.String(length=64), nullable=False),
        sa.Column("status", sa.String(length=32), nullable=False),
        sa.Column("input", postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column("output", postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column("error_code", sa.String(length=64), nullable=True),
        sa.Column("error_message", sa.Text(), nullable=True),
        sa.Column("started_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("finished_at", sa.DateTime(timezone=True), nullable=True),
    )
    op.create_index("ix_job_steps_job_id_name", "job_steps", ["job_id", "name"])
    op.create_table(
        "document_chunks",
        sa.Column("id", postgresql.UUID(as_uuid=False), primary_key=True),
        sa.Column("document_id", postgresql.UUID(as_uuid=False), sa.ForeignKey("documents.id"), nullable=False),
        sa.Column("chunk_index", sa.Integer(), nullable=False),
        sa.Column("content", sa.Text(), nullable=False),
        sa.Column("embedding", pgvector.sqlalchemy.Vector(dim=8), nullable=False),
        sa.Column("embedding_model", sa.String(length=128), nullable=False),
        sa.Column("token_count", sa.Integer(), nullable=False),
        sa.Column("metadata", postgresql.JSONB(astext_type=sa.Text()), nullable=False),
    )
    op.create_index("ix_document_chunks_document_id", "document_chunks", ["document_id"])
    op.create_table(
        "llm_usage",
        sa.Column("id", postgresql.UUID(as_uuid=False), primary_key=True),
        sa.Column("job_id", postgresql.UUID(as_uuid=False), sa.ForeignKey("jobs.id"), nullable=False),
        sa.Column("provider", sa.String(length=64), nullable=False),
        sa.Column("model", sa.String(length=128), nullable=False),
        sa.Column("operation", sa.String(length=64), nullable=False),
        sa.Column("input_tokens", sa.Integer(), nullable=False),
        sa.Column("output_tokens", sa.Integer(), nullable=False),
        sa.Column("estimated_cost", sa.Numeric(12, 6), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index("ix_llm_usage_job_id", "llm_usage", ["job_id"])


def downgrade() -> None:
    op.drop_index("ix_llm_usage_job_id", table_name="llm_usage")
    op.drop_table("llm_usage")
    op.drop_index("ix_document_chunks_document_id", table_name="document_chunks")
    op.drop_table("document_chunks")
    op.drop_index("ix_job_steps_job_id_name", table_name="job_steps")
    op.drop_table("job_steps")
    op.drop_table("documents")
    op.drop_index("ix_jobs_status_next_run_at", table_name="jobs")
    op.drop_table("jobs")
```

- [ ] **Step 6: Run tests and migration**

Run:

```bash
python -m pytest tests/domain/test_job_state.py -v
```

Expected: all state machine tests pass.

Run:

```bash
docker compose up -d postgres redis
python -m alembic upgrade head
```

Expected: migration applies without errors.

- [ ] **Step 7: Commit**

```bash
git add docker-compose.yml app alembic tests/domain/test_job_state.py
git commit -m "建立任務資料模型與狀態機"
```

---

## Task 3: Job Creation, Idempotency, And API

**FAANG evidence:** Shows API semantics for duplicate requests and payload mismatch, a common senior-level production concern.

**Files:**
- Create: `app/schemas.py`
- Create: `app/services/__init__.py`
- Create: `app/services/jobs.py`
- Create: `app/api/jobs.py`
- Modify: `app/main.py`
- Create: `tests/services/test_jobs.py`
- Create: `tests/api/test_jobs_api.py`

- [ ] **Step 1: Write failing service tests**

Create `tests/services/test_jobs.py`:

```python
import pytest

from app.services.jobs import IdempotencyConflictError, create_job


def test_create_job_returns_existing_job_for_same_key_and_same_payload(db_session):
    first = create_job(
        db_session,
        job_type="document_ingestion",
        idempotency_key="document:a:v1",
        payload={"sourceName": "a.md", "content": "hello"},
    )

    second = create_job(
        db_session,
        job_type="document_ingestion",
        idempotency_key="document:a:v1",
        payload={"sourceName": "a.md", "content": "hello"},
    )

    assert second.id == first.id


def test_create_job_rejects_same_key_with_different_payload(db_session):
    create_job(
        db_session,
        job_type="document_ingestion",
        idempotency_key="document:a:v1",
        payload={"sourceName": "a.md", "content": "hello"},
    )

    with pytest.raises(IdempotencyConflictError):
        create_job(
            db_session,
            job_type="document_ingestion",
            idempotency_key="document:a:v1",
            payload={"sourceName": "a.md", "content": "changed"},
        )
```

- [ ] **Step 2: Implement schemas and job service**

Create `app/schemas.py`:

```python
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
```

Create `app/services/__init__.py`:

```python
```

Create `app/services/jobs.py`:

```python
import hashlib
import json
from datetime import UTC, datetime
from uuid import uuid4

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.domain.job_state import JobStatus
from app.models import Job


class IdempotencyConflictError(Exception):
    pass


def _payload_hash(payload: dict) -> str:
    canonical = json.dumps(payload, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(canonical.encode("utf-8")).hexdigest()


def create_job(
    session: Session,
    *,
    job_type: str,
    idempotency_key: str,
    payload: dict,
    priority: int = 100,
) -> Job:
    payload_hash = _payload_hash(payload)
    existing = session.scalar(select(Job).where(Job.idempotency_key == idempotency_key))
    if existing is not None:
        if existing.payload_hash != payload_hash:
            raise IdempotencyConflictError("same idempotency key used with different payload")
        return existing

    now = datetime.now(UTC)
    job = Job(
        type=job_type,
        status=JobStatus.QUEUED.value,
        payload=payload,
        payload_hash=payload_hash,
        idempotency_key=idempotency_key,
        priority=priority,
        attempt_count=0,
        max_attempts=3,
        next_run_at=now,
        trace_id=uuid4().hex,
        created_at=now,
        updated_at=now,
    )
    session.add(job)
    session.commit()
    session.refresh(job)
    return job


def get_job(session: Session, job_id: str) -> Job | None:
    return session.get(Job, job_id)
```

- [ ] **Step 3: Write failing API tests**

Create `tests/api/test_jobs_api.py`:

```python
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
```

- [ ] **Step 4: Implement API router**

Create `app/api/jobs.py`:

```python
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_session
from app.schemas import CreateJobRequest, JobResponse
from app.services.jobs import IdempotencyConflictError, create_job, get_job

router = APIRouter(prefix="/jobs", tags=["jobs"])


@router.post("", response_model=JobResponse, status_code=status.HTTP_201_CREATED)
def post_job(request: CreateJobRequest, session: Session = Depends(get_session)) -> JobResponse:
    try:
        job = create_job(
            session,
            job_type=request.type,
            idempotency_key=request.idempotency_key,
            payload=request.payload,
            priority=request.priority,
        )
    except IdempotencyConflictError as exc:
        raise HTTPException(status_code=409, detail=str(exc)) from exc
    return JobResponse(
        id=job.id,
        type=job.type,
        status=job.status,
        trace_id=job.trace_id,
        attempt_count=job.attempt_count,
        max_attempts=job.max_attempts,
    )


@router.get("/{job_id}", response_model=JobResponse)
def get_job_by_id(job_id: str, session: Session = Depends(get_session)) -> JobResponse:
    job = get_job(session, job_id)
    if job is None:
        raise HTTPException(status_code=404, detail="job not found")
    return JobResponse(
        id=job.id,
        type=job.type,
        status=job.status,
        trace_id=job.trace_id,
        attempt_count=job.attempt_count,
        max_attempts=job.max_attempts,
    )
```

Modify `app/main.py`:

```python
from fastapi import FastAPI

from app.api.health import router as health_router
from app.api.jobs import router as jobs_router


def create_app() -> FastAPI:
    app = FastAPI(title="AI Job Orchestrator")
    app.include_router(health_router)
    app.include_router(jobs_router)
    return app


app = create_app()
```

- [ ] **Step 5: Run tests**

Run:

```bash
python -m pytest tests/services/test_jobs.py tests/api/test_jobs_api.py -v
```

Expected: all tests pass.

- [ ] **Step 6: Commit**

```bash
git add app tests/services/test_jobs.py tests/api/test_jobs_api.py
git commit -m "加入任務建立與冪等控制"
```

---

## Task 4: Retry Policy And Worker Execution

**FAANG evidence:** Shows how transient failures, retry backoff, and dead lettering are handled without manual intervention.

**Files:**
- Create: `app/domain/retry_policy.py`
- Create: `app/workers/__init__.py`
- Create: `app/workers/celery_app.py`
- Create: `app/workers/tasks.py`
- Create: `tests/domain/test_retry_policy.py`
- Create: `tests/services/test_worker_execution.py`

- [ ] **Step 1: Write retry policy tests**

Create `tests/domain/test_retry_policy.py`:

```python
from app.domain.retry_policy import next_retry_delay_seconds


def test_retry_delay_uses_exponential_backoff():
    assert next_retry_delay_seconds(attempt_count=1) == 2
    assert next_retry_delay_seconds(attempt_count=2) == 4
    assert next_retry_delay_seconds(attempt_count=3) == 8


def test_retry_delay_is_capped():
    assert next_retry_delay_seconds(attempt_count=20) == 300
```

- [ ] **Step 2: Implement retry policy**

Create `app/domain/retry_policy.py`:

```python
def next_retry_delay_seconds(*, attempt_count: int, cap_seconds: int = 300) -> int:
    delay = 2**attempt_count
    return min(delay, cap_seconds)
```

- [ ] **Step 3: Add worker execution tests**

Create `tests/services/test_worker_execution.py`:

```python
from app.domain.job_state import JobStatus
from app.services.jobs import create_job, get_job
from app.workers.tasks import execute_job_once


def test_worker_marks_successful_job_completed(db_session, fake_embedding_provider):
    job = create_job(
        db_session,
        job_type="document_ingestion",
        idempotency_key="document:a:v1",
        payload={"sourceName": "a.md", "content": "hello world"},
    )

    execute_job_once(db_session, job.id, embedding_provider=fake_embedding_provider)

    updated = get_job(db_session, job.id)
    assert updated.status == JobStatus.COMPLETED.value


def test_worker_moves_job_to_dead_letter_after_max_attempts(db_session, failing_embedding_provider):
    job = create_job(
        db_session,
        job_type="document_ingestion",
        idempotency_key="document:a:v1",
        payload={"sourceName": "a.md", "content": "hello world"},
    )
    job.max_attempts = 1
    db_session.commit()

    execute_job_once(db_session, job.id, embedding_provider=failing_embedding_provider)

    updated = get_job(db_session, job.id)
    assert updated.status == JobStatus.DEAD_LETTERED.value
```

- [ ] **Step 4: Implement Celery app and task entrypoint**

Create `app/workers/__init__.py`:

```python
```

Create `app/workers/celery_app.py`:

```python
from celery import Celery

from app.config import Settings

settings = Settings()

celery_app = Celery("ai_job_orchestrator", broker=settings.redis_url, backend=settings.redis_url)
celery_app.conf.task_acks_late = True
celery_app.conf.worker_prefetch_multiplier = 1
```

Create `app/workers/tasks.py`:

```python
from datetime import UTC, datetime, timedelta

from sqlalchemy.orm import Session

from app.database import SessionLocal
from app.domain.job_state import JobStatus
from app.domain.retry_policy import next_retry_delay_seconds
from app.models import Job
from app.providers.embeddings import EmbeddingProvider, FakeEmbeddingProvider
from app.services.ingestion import ingest_document
from app.workers.celery_app import celery_app


def execute_job_once(
    session: Session,
    job_id: str,
    *,
    embedding_provider: EmbeddingProvider | None = None,
) -> None:
    provider = embedding_provider or FakeEmbeddingProvider()
    job = session.get(Job, job_id)
    if job is None or job.status not in {JobStatus.QUEUED.value, JobStatus.RETRYING.value}:
        return

    now = datetime.now(UTC)
    job.status = JobStatus.RUNNING.value
    job.attempt_count += 1
    job.updated_at = now
    session.commit()

    try:
        if job.type == "document_ingestion":
            ingest_document(session, job=job, embedding_provider=provider)
        job.status = JobStatus.COMPLETED.value
        job.updated_at = datetime.now(UTC)
        session.commit()
    except Exception:
        if job.attempt_count >= job.max_attempts:
            job.status = JobStatus.DEAD_LETTERED.value
        else:
            delay = next_retry_delay_seconds(attempt_count=job.attempt_count)
            job.status = JobStatus.RETRYING.value
            job.next_run_at = datetime.now(UTC) + timedelta(seconds=delay)
        job.updated_at = datetime.now(UTC)
        session.commit()


@celery_app.task(name="execute_job")
def execute_job(job_id: str) -> None:
    with SessionLocal() as session:
        execute_job_once(session, job_id)
```

- [ ] **Step 5: Run tests**

Run:

```bash
python -m pytest tests/domain/test_retry_policy.py tests/services/test_worker_execution.py -v
```

Expected: all tests pass. If this task is executed before Task 5, first create the ingestion files from Task 5 in the same checkpoint, then run this command.

- [ ] **Step 6: Commit after Task 5 passes**

```bash
git add app tests/domain/test_retry_policy.py tests/services/test_worker_execution.py
git commit -m "加入任務重試與 worker 執行流程"
```

---

## Task 5: Document Ingestion, Chunking, And Usage Tracking

**FAANG evidence:** Shows idempotent step design and deterministic AI workload behavior that can be tested without external LLM calls.

**Files:**
- Create: `app/domain/chunking.py`
- Create: `app/providers/__init__.py`
- Create: `app/providers/embeddings.py`
- Create: `app/services/ingestion.py`
- Create: `tests/domain/test_chunking.py`
- Create: `tests/services/test_ingestion.py`
- Modify: `tests/conftest.py`

- [ ] **Step 1: Write chunking tests**

Create `tests/domain/test_chunking.py`:

```python
from app.domain.chunking import chunk_text


def test_chunk_text_splits_by_word_count():
    chunks = chunk_text("one two three four five six", max_words=3)

    assert chunks == ["one two three", "four five six"]


def test_chunk_text_removes_empty_whitespace():
    chunks = chunk_text("  one   two\n\nthree  ", max_words=2)

    assert chunks == ["one two", "three"]
```

- [ ] **Step 2: Implement chunking**

Create `app/domain/chunking.py`:

```python
def chunk_text(content: str, *, max_words: int = 120) -> list[str]:
    words = content.split()
    return [" ".join(words[index : index + max_words]) for index in range(0, len(words), max_words)]
```

- [ ] **Step 3: Implement embedding provider abstraction**

Create `app/providers/__init__.py`:

```python
```

Create `app/providers/embeddings.py`:

```python
import hashlib
from typing import Protocol


class EmbeddingProvider(Protocol):
    model: str
    provider: str

    def embed(self, text: str) -> list[float]:
        pass


class FakeEmbeddingProvider:
    model = "fake-embedding-v1"
    provider = "fake"

    def embed(self, text: str) -> list[float]:
        digest = hashlib.sha256(text.encode("utf-8")).digest()
        return [round(digest[index] / 255, 6) for index in range(8)]


class FailingEmbeddingProvider:
    model = "failing-embedding-v1"
    provider = "fake"

    def embed(self, text: str) -> list[float]:
        raise TimeoutError("embedding provider timeout")
```

- [ ] **Step 4: Write ingestion service test**

Create `tests/services/test_ingestion.py`:

```python
from sqlalchemy import select

from app.models import Document, DocumentChunk, LlmUsage
from app.providers.embeddings import FakeEmbeddingProvider
from app.services.ingestion import ingest_document
from app.services.jobs import create_job


def test_ingest_document_creates_document_chunks_and_usage(db_session):
    job = create_job(
        db_session,
        job_type="document_ingestion",
        idempotency_key="document:a:v1",
        payload={"sourceName": "a.md", "content": "one two three four"},
    )

    ingest_document(db_session, job=job, embedding_provider=FakeEmbeddingProvider())

    document = db_session.scalar(select(Document))
    chunks = db_session.scalars(select(DocumentChunk).order_by(DocumentChunk.chunk_index)).all()
    usage = db_session.scalar(select(LlmUsage))

    assert document.source_name == "a.md"
    assert [chunk.content for chunk in chunks] == ["one two three four"]
    assert chunks[0].embedding_model == "fake-embedding-v1"
    assert usage.operation == "embedding"
    assert usage.input_tokens == 4
```

- [ ] **Step 5: Implement ingestion service**

Create `app/services/ingestion.py`:

```python
import hashlib
from datetime import UTC, datetime

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.domain.chunking import chunk_text
from app.models import Document, DocumentChunk, Job, JobStep, LlmUsage
from app.providers.embeddings import EmbeddingProvider


def _content_hash(content: str) -> str:
    return hashlib.sha256(content.encode("utf-8")).hexdigest()


def ingest_document(session: Session, *, job: Job, embedding_provider: EmbeddingProvider) -> None:
    payload = job.payload
    source_name = str(payload["sourceName"])
    content = str(payload["content"])
    content_hash = _content_hash(content)
    now = datetime.now(UTC)

    document = session.scalar(select(Document).where(Document.content_hash == content_hash))
    if document is None:
        document = Document(
            source_name=source_name,
            content_hash=content_hash,
            metadata={"source": source_name},
            created_at=now,
        )
        session.add(document)
        session.flush()

    chunks = chunk_text(content)
    input_tokens = 0
    for index, chunk in enumerate(chunks):
        token_count = len(chunk.split())
        input_tokens += token_count
        session.add(
            DocumentChunk(
                document_id=document.id,
                chunk_index=index,
                content=chunk,
                embedding=embedding_provider.embed(chunk),
                embedding_model=embedding_provider.model,
                token_count=token_count,
                metadata={"traceId": job.trace_id},
            )
        )

    session.add(
        JobStep(
            job_id=job.id,
            name="document_ingestion",
            status="completed",
            input={"sourceName": source_name},
            output={"documentId": document.id, "chunkCount": len(chunks)},
            started_at=now,
            finished_at=datetime.now(UTC),
        )
    )
    session.add(
        LlmUsage(
            job_id=job.id,
            provider=embedding_provider.provider,
            model=embedding_provider.model,
            operation="embedding",
            input_tokens=input_tokens,
            output_tokens=0,
            estimated_cost=0,
            created_at=datetime.now(UTC),
        )
    )
    session.commit()
```

- [ ] **Step 6: Add test fixtures**

Replace `tests/conftest.py` with:

```python
import os
from collections.abc import Generator

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, text
from sqlalchemy.orm import Session, sessionmaker

from app.database import Base, get_session
from app.main import create_app
from app.providers.embeddings import FailingEmbeddingProvider, FakeEmbeddingProvider

TEST_DATABASE_URL = os.getenv(
    "TEST_DATABASE_URL",
    "postgresql+psycopg://postgres:postgres@localhost:5432/ai_jobs",
)


@pytest.fixture()
def db_session() -> Generator[Session, None, None]:
    engine = create_engine(TEST_DATABASE_URL, pool_pre_ping=True)
    with engine.begin() as connection:
        connection.execute(text("CREATE EXTENSION IF NOT EXISTS vector"))
    Base.metadata.drop_all(engine)
    Base.metadata.create_all(engine)
    TestingSessionLocal = sessionmaker(bind=engine, autoflush=False, expire_on_commit=False)
    with TestingSessionLocal() as session:
        yield session
    Base.metadata.drop_all(engine)


@pytest.fixture()
def client(db_session: Session) -> Generator[TestClient, None, None]:
    app = create_app()

    def override_get_session() -> Generator[Session, None, None]:
        yield db_session

    app.dependency_overrides[get_session] = override_get_session
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()


@pytest.fixture()
def fake_embedding_provider() -> FakeEmbeddingProvider:
    return FakeEmbeddingProvider()


@pytest.fixture()
def failing_embedding_provider() -> FailingEmbeddingProvider:
    return FailingEmbeddingProvider()
```

- [ ] **Step 7: Run tests**

Run:

```bash
python -m pytest tests/domain/test_chunking.py tests/services/test_ingestion.py tests/services/test_worker_execution.py -v
```

Expected: all tests pass.

- [ ] **Step 8: Commit**

```bash
git add app tests
git commit -m "加入文件 ingestion 與 embedding 抽象"
```

---

## Task 6: Retrieval API

**FAANG evidence:** Shows retrieval can be evaluated and observed independently from generation, which is stronger than a chatbot demo.

**Files:**
- Create: `app/services/retrieval.py`
- Create: `app/api/retrieval.py`
- Modify: `app/main.py`
- Create: `tests/api/test_retrieval_api.py`

- [ ] **Step 1: Write retrieval API test**

Create `tests/api/test_retrieval_api.py`:

```python
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

    from app.workers.tasks import execute_job_once

    execute_job_once(db_session, job_id, embedding_provider=fake_embedding_provider)

    response = client.post("/retrieval/query", json={"query": "retry timeout", "topK": 3})

    assert response.status_code == 200
    body = response.json()
    assert body["results"][0]["content"] == "latency budget retry timeout"
    assert body["results"][0]["score"] >= 0
```

- [ ] **Step 2: Implement retrieval service**

Create `app/services/retrieval.py`:

```python
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import DocumentChunk
from app.providers.embeddings import EmbeddingProvider


def _cosine_like_score(left: list[float], right: list[float]) -> float:
    return round(sum(a * b for a, b in zip(left, right, strict=True)), 6)


def query_chunks(
    session: Session,
    *,
    query: str,
    top_k: int,
    embedding_provider: EmbeddingProvider,
) -> list[dict]:
    query_embedding = embedding_provider.embed(query)
    chunks = session.scalars(select(DocumentChunk)).all()
    ranked = sorted(
        (
            {
                "documentId": chunk.document_id,
                "chunkId": chunk.id,
                "content": chunk.content,
                "score": _cosine_like_score(query_embedding, chunk.embedding),
            }
            for chunk in chunks
        ),
        key=lambda item: item["score"],
        reverse=True,
    )
    return ranked[:top_k]
```

- [ ] **Step 3: Implement retrieval API**

Create `app/api/retrieval.py`:

```python
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_session
from app.providers.embeddings import FakeEmbeddingProvider
from app.schemas import RetrievalRequest
from app.services.retrieval import query_chunks

router = APIRouter(prefix="/retrieval", tags=["retrieval"])


@router.post("/query")
def query_retrieval(request: RetrievalRequest, session: Session = Depends(get_session)) -> dict:
    results = query_chunks(
        session,
        query=request.query,
        top_k=request.top_k,
        embedding_provider=FakeEmbeddingProvider(),
    )
    return {"results": results}
```

Modify `app/main.py`:

```python
from fastapi import FastAPI

from app.api.health import router as health_router
from app.api.jobs import router as jobs_router
from app.api.retrieval import router as retrieval_router


def create_app() -> FastAPI:
    app = FastAPI(title="AI Job Orchestrator")
    app.include_router(health_router)
    app.include_router(jobs_router)
    app.include_router(retrieval_router)
    return app


app = create_app()
```

- [ ] **Step 4: Run tests**

Run:

```bash
python -m pytest tests/api/test_retrieval_api.py -v
```

Expected: all tests pass.

- [ ] **Step 5: Commit**

```bash
git add app tests/api/test_retrieval_api.py
git commit -m "加入 retrieval 查詢 API"
```

---

## Task 7: Observability, Load Test, And README Evidence

**FAANG evidence:** Turns the project from "it works locally" into a portfolio artifact with measured behavior and production discussion points.

**Files:**
- Create: `app/observability.py`
- Create: `scripts/load_test.py`
- Modify: `app/main.py`
- Modify: `app/services/jobs.py`
- Modify: `app/workers/tasks.py`
- Modify: `readme.md`

- [ ] **Step 1: Add observability helpers**

Create `app/observability.py`:

```python
import logging


def configure_logging() -> None:
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s trace_id=%(trace_id)s %(message)s",
    )


def log_event(logger: logging.Logger, *, trace_id: str, event: str, **fields: object) -> None:
    details = " ".join(f"{key}={value}" for key, value in sorted(fields.items()))
    logger.info("%s %s", event, details, extra={"trace_id": trace_id})
```

- [ ] **Step 2: Wire logging into app and worker**

Modify `app/main.py`:

```python
from fastapi import FastAPI

from app.api.health import router as health_router
from app.api.jobs import router as jobs_router
from app.api.retrieval import router as retrieval_router
from app.observability import configure_logging


def create_app() -> FastAPI:
    configure_logging()
    app = FastAPI(title="AI Job Orchestrator")
    app.include_router(health_router)
    app.include_router(jobs_router)
    app.include_router(retrieval_router)
    return app


app = create_app()
```

Replace `app/workers/tasks.py` with this version:

```python
import logging
from datetime import UTC, datetime, timedelta

from sqlalchemy.orm import Session

from app.database import SessionLocal
from app.domain.job_state import JobStatus
from app.domain.retry_policy import next_retry_delay_seconds
from app.models import Job
from app.observability import log_event
from app.providers.embeddings import EmbeddingProvider, FakeEmbeddingProvider
from app.services.ingestion import ingest_document
from app.workers.celery_app import celery_app

logger = logging.getLogger(__name__)


def execute_job_once(
    session: Session,
    job_id: str,
    *,
    embedding_provider: EmbeddingProvider | None = None,
) -> None:
    provider = embedding_provider or FakeEmbeddingProvider()
    job = session.get(Job, job_id)
    if job is None or job.status not in {JobStatus.QUEUED.value, JobStatus.RETRYING.value}:
        return

    now = datetime.now(UTC)
    job.status = JobStatus.RUNNING.value
    job.attempt_count += 1
    job.updated_at = now
    session.commit()
    log_event(
        logger,
        trace_id=job.trace_id,
        event="job_started",
        job_id=job.id,
        attempt_count=job.attempt_count,
        status=job.status,
    )

    try:
        if job.type == "document_ingestion":
            ingest_document(session, job=job, embedding_provider=provider)
        job.status = JobStatus.COMPLETED.value
        job.updated_at = datetime.now(UTC)
        session.commit()
        log_event(
            logger,
            trace_id=job.trace_id,
            event="job_completed",
            job_id=job.id,
            attempt_count=job.attempt_count,
            status=job.status,
        )
    except Exception:
        if job.attempt_count >= job.max_attempts:
            job.status = JobStatus.DEAD_LETTERED.value
            event = "job_dead_lettered"
        else:
            delay = next_retry_delay_seconds(attempt_count=job.attempt_count)
            job.status = JobStatus.RETRYING.value
            job.next_run_at = datetime.now(UTC) + timedelta(seconds=delay)
            event = "job_retrying"
        job.updated_at = datetime.now(UTC)
        session.commit()
        log_event(
            logger,
            trace_id=job.trace_id,
            event=event,
            job_id=job.id,
            attempt_count=job.attempt_count,
            status=job.status,
        )


@celery_app.task(name="execute_job")
def execute_job(job_id: str) -> None:
    with SessionLocal() as session:
        execute_job_once(session, job_id)
```

- [ ] **Step 3: Create load test script**

Create `scripts/load_test.py`:

```python
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
            if response.status_code not in {201, 200}:
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
```

- [ ] **Step 4: Update README with evidence sections**

Append this exact section to `readme.md`:

```markdown
## 本機啟動

```bash
docker compose up -d postgres redis
python -m alembic upgrade head
python -m uvicorn app.main:app --reload
celery -A app.workers.celery_app.celery_app worker --loglevel=info
```

## 測試證據

```bash
python -m pytest -v
python -m ruff check .
```

## FAANG 面試講法

- 我把 HTTP request 與長時間 AI workload 解耦，避免同步 request timeout。
- Postgres 是 job state 的 source of truth，Redis/Celery 只負責 dispatch。
- idempotency key 搭配 payload hash，避免 client retry 造成重複資料或語意衝突。
- worker 使用 retry backoff 與 dead letter 狀態處理 transient failure。
- trace id 串起 API、worker、step、LLM usage，方便排查 production issue。
```

- [ ] **Step 5: Run verification**

Run:

```bash
python -m pytest -v
python -m ruff check .
```

Expected: tests pass and lint passes.

- [ ] **Step 6: Commit**

```bash
git add app scripts readme.md
git commit -m "補齊觀測性與面試證據"
```

---

## Self-Review

### Spec Coverage

- Job creation: covered by Task 3.
- Job state machine: covered by Task 2.
- Idempotency: covered by Task 3.
- Retry and dead letter handling: covered by Task 4.
- Worker execution: covered by Task 4.
- Document ingestion: covered by Task 5.
- Embedding abstraction: covered by Task 5.
- Retrieval API: covered by Task 6.
- Observability: covered by Task 7.
- README and FAANG interview framing: covered by Task 7.
- Docker Compose local environment: covered by Task 2.

### Known Scope Control

- Real OpenAI/Anthropic embedding calls are intentionally outside MVP. The provider interface makes it easy to add later, while deterministic fake embeddings make tests reliable.
- A full dashboard is outside MVP. README evidence, logs, API responses, and load test output are enough for the first portfolio version.
- Kafka is outside MVP. The README should explain why Redis/Celery is acceptable for a single-service portfolio system and where Kafka becomes useful.

### Execution Order

Implement tasks in order. Task 4's worker test depends on Task 5's ingestion service, so Task 4 can add the retry policy and worker shell first, then the full test should pass after Task 5. Commit Task 4 only after Task 5 makes the worker path executable, or combine Task 4 and Task 5 into one checkpoint if using inline execution.
