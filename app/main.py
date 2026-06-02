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
