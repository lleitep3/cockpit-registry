import structlog
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.schemas.item import ItemCreate, ItemRead, ItemUpdate
from app.services import item_service

logger = structlog.get_logger()
router = APIRouter(prefix="/items")


@router.get("/", response_model=list[ItemRead])
async def list_items(
    skip: int = 0,
    limit: int = 20,
    db: AsyncSession = Depends(get_db),
):
    """Lista todos os items com paginação."""
    logger.info("list_items", skip=skip, limit=limit)
    return await item_service.list_items(db, skip=skip, limit=limit)


@router.post("/", response_model=ItemRead, status_code=status.HTTP_201_CREATED)
async def create_item(data: ItemCreate, db: AsyncSession = Depends(get_db)):
    """Cria um novo item."""
    return await item_service.create_item(db, data)


@router.get("/{item_id}", response_model=ItemRead)
async def get_item(item_id: int, db: AsyncSession = Depends(get_db)):
    """Busca um item pelo ID."""
    item = await item_service.get_item(db, item_id)
    if not item:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Item não encontrado")
    return item


@router.patch("/{item_id}", response_model=ItemRead)
async def update_item(
    item_id: int,
    data: ItemUpdate,
    db: AsyncSession = Depends(get_db),
):
    """Atualiza parcialmente um item."""
    item = await item_service.get_item(db, item_id)
    if not item:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Item não encontrado")
    return await item_service.update_item(db, item, data)


@router.delete("/{item_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_item(item_id: int, db: AsyncSession = Depends(get_db)):
    """Remove um item pelo ID."""
    item = await item_service.get_item(db, item_id)
    if not item:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Item não encontrado")
    await item_service.delete_item(db, item)
