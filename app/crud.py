from typing import List, Optional

from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession

from . import models, schemas


async def create_history_record(
        db: AsyncSession,
        record: schemas.HistoryCreate
        ) -> models.History:
    """Создает и сохраняет новую запись в истории."""
    db_record = models.History(**record.model_dump())
    db.add(db_record)
    await db.commit()
    await db.refresh(db_record)
    return db_record


async def get_all_history(
        db: AsyncSession,
        skip: int = 0, limit: int = 100
        ) -> List[models.History]:
    """Возвращает все записи из истории с пагинацией."""
    result = await db.execute(select(models.History).offset(skip).limit(limit))
    return result.scalars().all()


async def get_history_by_cadastral(
        db: AsyncSession,
        cadastral_number: str
        ) -> List[models.History]:
    """Возвращает все записи по конкретному кадастровому номеру."""
    result = await db.execute(
        select(models.History).filter(
            models.History.cadastral_number == cadastral_number)
    )
    return result.scalars().all()


async def delete_all_history(db: AsyncSession) -> None:
    """Удаляет все записи в таблице с историей."""
    await db.execute(delete(models.History))
    await db.commit()


async def delete_history_record_by_id(
        db: AsyncSession,
        record_id: int
        ) -> Optional[models.History]:
    """Удаляет конкретную запись в таблице с историей."""
    record_to_delete = await db.get(models.History, record_id)
    if not record_to_delete:
        return None

    await db.delete(record_to_delete)
    await db.commit()
    return record_to_delete
