import structlog
from fastapi import APIRouter
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import Depends

from app.core.database import get_db

logger = structlog.get_logger()
router = APIRouter()


@router.get("/health")
async def health(db: AsyncSession = Depends(get_db)):
    """Healthcheck: verifica se a API e o banco estão ok."""
    try:
        await db.execute(text("SELECT 1"))
        db_status = "ok"
    except Exception as e:
        logger.error("healthcheck_db_error", error=str(e))
        db_status = "error"

    return {"status": "ok", "db": db_status}
