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


from pydantic import BaseModel
import pathlib

class DocumentUpdate(BaseModel):
    path: str
    content: str

@router.put("/document")
async def update_document(update: DocumentUpdate) -> dict[str, Any]:
    """Atualiza o conteúdo de um documento."""
    path = pathlib.Path(update.path)
    if path.is_file():
        path.write_text(update.content, encoding="utf-8")
    return {"status": "ok"}
