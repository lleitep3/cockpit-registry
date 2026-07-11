import structlog
from fastapi import APIRouter

logger = structlog.get_logger()
router = APIRouter()


@router.get("/health")
async def health():
    """Healthcheck: verifica se a API está ok."""
    return {"status": "ok"}
