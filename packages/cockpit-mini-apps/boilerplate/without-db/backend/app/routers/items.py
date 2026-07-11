"""CRUD em memória (sem banco de dados).

Os dados são perdidos quando o container é reiniciado.
Substitua por persistência real se necessário.
"""
from datetime import datetime, timezone

import structlog
from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel

logger = structlog.get_logger()
router = APIRouter(prefix="/items")

# Store em memória
_items: dict[int, dict] = {}
_next_id = 1


class ItemCreate(BaseModel):
    name: str
    description: str | None = None


class ItemUpdate(BaseModel):
    name: str | None = None
    description: str | None = None


class ItemRead(BaseModel):
    id: int
    name: str
    description: str | None
    created_at: str
    updated_at: str


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


@router.get("/", response_model=list[ItemRead])
async def list_items(skip: int = 0, limit: int = 20):
    """Lista todos os items com paginação."""
    all_items = list(_items.values())
    return all_items[skip : skip + limit]


@router.post("/", response_model=ItemRead, status_code=status.HTTP_201_CREATED)
async def create_item(data: ItemCreate):
    """Cria um novo item."""
    global _next_id
    now = _now()
    item = {
        "id": _next_id,
        "name": data.name,
        "description": data.description,
        "created_at": now,
        "updated_at": now,
    }
    _items[_next_id] = item
    _next_id += 1
    logger.info("item_created", item_id=item["id"], name=item["name"])
    return item


@router.get("/{item_id}", response_model=ItemRead)
async def get_item(item_id: int):
    """Busca um item pelo ID."""
    if item_id not in _items:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Item não encontrado")
    return _items[item_id]


@router.patch("/{item_id}", response_model=ItemRead)
async def update_item(item_id: int, data: ItemUpdate):
    """Atualiza parcialmente um item."""
    if item_id not in _items:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Item não encontrado")
    item = _items[item_id]
    if data.name is not None:
        item["name"] = data.name
    if data.description is not None:
        item["description"] = data.description
    item["updated_at"] = _now()
    logger.info("item_updated", item_id=item_id)
    return item


@router.delete("/{item_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_item(item_id: int):
    """Remove um item pelo ID."""
    if item_id not in _items:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Item não encontrado")
    del _items[item_id]
    logger.info("item_deleted", item_id=item_id)
