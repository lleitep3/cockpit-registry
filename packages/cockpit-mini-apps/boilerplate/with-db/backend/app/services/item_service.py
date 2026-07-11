import structlog
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.item import Item
from app.schemas.item import ItemCreate, ItemUpdate

logger = structlog.get_logger()


async def list_items(db: AsyncSession, skip: int = 0, limit: int = 20) -> list[Item]:
    result = await db.execute(select(Item).offset(skip).limit(limit).order_by(Item.id))
    return list(result.scalars().all())


async def get_item(db: AsyncSession, item_id: int) -> Item | None:
    return await db.get(Item, item_id)


async def create_item(db: AsyncSession, data: ItemCreate) -> Item:
    item = Item(**data.model_dump())
    db.add(item)
    await db.commit()
    await db.refresh(item)
    logger.info("item_created", item_id=item.id, name=item.name)
    return item


async def update_item(db: AsyncSession, item: Item, data: ItemUpdate) -> Item:
    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(item, field, value)
    await db.commit()
    await db.refresh(item)
    logger.info("item_updated", item_id=item.id)
    return item


async def delete_item(db: AsyncSession, item: Item) -> None:
    await db.delete(item)
    await db.commit()
    logger.info("item_deleted", item_id=item.id)
