from typing import Any

from fastapi import APIRouter, Query

from app.services.log_analyzer import analyze_metrics, load_logs, load_metrics

router = APIRouter(prefix="/logs", tags=["logs"])


@router.get("/metrics")
async def get_metrics(limit: int = Query(10000, ge=1, le=50000)) -> dict[str, Any]:
    """Retorna métricas brutas de execução de comandos."""
    return {"metrics": load_metrics(limit=limit)}


@router.get("/insights")
async def get_insights(limit: int = Query(10000, ge=1, le=50000)) -> dict[str, Any]:
    """Retorna insights agregados das métricas de execução."""
    metrics = load_metrics(limit=limit)
    return analyze_metrics(metrics)


@router.get("")
async def get_logs(limit: int = Query(1000, ge=1, le=5000)) -> dict[str, Any]:
    """Retorna entradas recentes dos arquivos de log."""
    return {"logs": load_logs(limit=limit)}
