from fastapi import APIRouter

from app.config import Settings

router = APIRouter()


@router.get("/health")
def health() -> dict[str, str]:
    settings = Settings()
    return {"status": "ok", "service": settings.service_name}
