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

from pydantic import BaseModel

class DiagnoseRequest(BaseModel):
    command: str
    error_msg: str
    error_type: str
    args: list[str]

@router.post("/diagnose")
async def diagnose_failure(req: DiagnoseRequest) -> dict[str, Any]:
    """IA auto-diagnoses the failure and suggests a prompt to fix it."""
    prompt = f"""Preciso de ajuda para corrigir um erro que ocorreu ao rodar o comando:
`{req.command} {' '.join(req.args)}`

**Tipo de Erro:** `{req.error_type}`
**Mensagem de Erro:**
```
{req.error_msg}
```

Por favor, analise este erro na base de código, verifique os logs e arquivos envolvidos, e aplique a correção necessária."""

    return {
        "diagnosis": "Para investigar e corrigir este erro de forma inteligente, copie o prompt abaixo e cole no chat com a IA (Antigravity). Ela terá todo o contexto necessário para resolver o problema.",
        "suggested_fix": prompt,
        "kb_reference": None
    }


class ResolveRequest(BaseModel):
    timestamp: str

@router.post("/resolve")
async def resolve_error(req: ResolveRequest) -> dict[str, Any]:
    from app.services.log_analyzer import save_resolution
    save_resolution(req.timestamp)
    return {"success": True}
