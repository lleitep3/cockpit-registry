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
    """IA auto-diagnoses the failure and suggests a fix script."""
    # TODO: Implement actual LLM call here fetching context from KB
    # For now, we mock the response based on the command and error
    
    if "doctor" in req.command and "Vault not found" in req.error_msg:
        return {
            "diagnosis": "A pasta 'vault' requerida pelo sistema não foi encontrada no diretório .cockpit. Isso geralmente acontece após uma deleção manual ou falha no setup.",
            "suggested_fix": "cockpit setup",
            "kb_reference": "wiki/troubleshooting/missing-vault.md"
        }
        
    return {
        "diagnosis": f"Análise da IA: O comando '{req.command}' falhou com '{req.error_msg}'. Nenhuma solução exata foi encontrada na Knowledge Base.",
        "suggested_fix": "cockpit doctor",
        "kb_reference": None
    }


class AutoFixRequest(BaseModel):
    command: str

@router.post("/autofix")
async def execute_autofix(req: AutoFixRequest) -> dict[str, Any]:
    import shlex
    import asyncio
    
    if not req.command.startswith("cockpit "):
        return {"success": False, "error": "Only cockpit commands are allowed"}
    
    cmd = shlex.split(req.command)
    try:
        proc = await asyncio.create_subprocess_exec(
            *cmd,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )
        stdout, stderr = await proc.communicate()
        return {
            "success": proc.returncode == 0,
            "stdout": stdout.decode(),
            "stderr": stderr.decode(),
            "returncode": proc.returncode
        }
    except Exception as e:
        return {"success": False, "error": str(e)}
