from celery import Celery

from app.config import Settings

settings = Settings()

celery_app = Celery("ai_job_orchestrator", broker=settings.redis_url, backend=settings.redis_url)
celery_app.conf.task_acks_late = True
celery_app.conf.worker_prefetch_multiplier = 1
