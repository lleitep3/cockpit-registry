from __future__ import annotations

from typing import Any

from fastapi import APIRouter, Query

from app.services.cockpit_reader import list_kb
from app.services.kb_graph import build_kb_graph, search_kb

router = APIRouter(prefix="/kb", tags=["kb"])


@router.get("")
async def get_kb() -> dict[str, Any]:
    """Lista todos os documentos do KB."""
    return {"documents": list_kb()}


@router.get("/graph")
async def get_graph() -> dict[str, Any]:
    """Retorna grafo de notas e links."""
    return build_kb_graph()


@router.get("/search")
async def search(query: str = Query(..., min_length=1)) -> dict[str, Any]:
    """Busca documentos no KB."""
    return {"results": search_kb(query)}
