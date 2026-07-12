from typing import Any

from fastapi import APIRouter

from app.core.command_executor import run_doctor
from app.services.cockpit_reader import list_kb, list_packages, list_registries
from app.services.log_analyzer import analyze_metrics, load_metrics

router = APIRouter(prefix="/overview", tags=["overview"])


@router.get("/doctor")
async def doctor() -> dict[str, Any]:
    """Executa e retorna o resultado do `cockpit doctor --json`."""
    return run_doctor()


@router.get("/kpi")
async def kpi() -> dict[str, Any]:
    """Retorna KPIs agregados para a página inicial."""
    metrics = load_metrics(limit=10000)
    insights = analyze_metrics(metrics)
    packages = list_packages()
    kb = list_kb()
    registries = list_registries()

    return {
        "vault_locked": False,  # placeholder until vault module is implemented
        "packages_total": len(packages),
        "packages_upgradable": 0,  # requires registry comparison
        "mini_apps_total": 0,  # requires mini-apps module
        "mini_apps_active": 0,
        "kb_total": len(kb),
        "kb_connections": 0,  # requires graph analysis
        "executions_total": insights["total"],
        "executions_success_rate": insights["success_rate"],
        "executions_failed": insights["failed"],
    }
