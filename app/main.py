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
