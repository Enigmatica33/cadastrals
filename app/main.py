import asyncio
import random
from typing import List

import httpx
from fastapi import Depends, FastAPI, HTTPException, Query, status
from fastapi.responses import JSONResponse
from sqlalchemy.ext.asyncio import AsyncSession

from . import crud, schemas
from .database import get_db

app = FastAPI(
    title="Cadaster Service",
    description="Сервис для эмуляции запросов к внешнему кадастровому серверу."
)


@app.get("/ping")
async def ping():
    """Проверка, что сервер запущен."""
    return {"ping": "pong!"}


@app.get("/result", summary="Эмуляция внешнего сервера")
async def emulate_external_server():
    """
    Эмулирует долгий ответ от внешнего сервера.
    Обработка занимает от 1 до 60 секунд.
    Возвращает случайный результат: true или false.
    """
    delay = random.randint(1, 60)
    await asyncio.sleep(delay)
    result = random.choice([True, False])
    return {"result": result}


@app.post(
        "/query",
        response_model=schemas.History,
        summary="Отправка запроса на создание записи",
        status_code=status.HTTP_201_CREATED
        )
async def create_query(
    query_data: schemas.QueryRequest,
    db: AsyncSession = Depends(get_db)
):
    """
    Принимает кадастровый номер и координаты, эмулирует запрос
    к внешнему серверу, сохраняет результат в БД и возвращает его.
    """
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(
                "http://127.0.0.1:8000/result",
                timeout=65.0
                )
            response.raise_for_status()
            server_response_data = response.json()
            server_result = server_response_data.get("result")

    except httpx.RequestError as e:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Ошибка при запросе к внешнему серверу: {e}"
            )

    if server_result is None:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Внешний сервер вернул некорректный ответ."
            )
    if server_result is True:
        history_record_in = schemas.HistoryCreate(
            **query_data.model_dump(),
            server_response=server_result
        )

        created_record = await crud.create_history_record(
            db=db,
            record=history_record_in
            )
        return created_record
    else:
        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content={
                "message": "Внешний сервер вернул False. Запись не создана.",
                "cadastral_number": query_data.cadastral_number,
                "server_response": False
            }
        )


@app.get(
        "/history",
        response_model=List[schemas.History],
        summary="Получение истории запросов",
        status_code=status.HTTP_200_OK
        )
async def read_history(
    cadastral_number: str | None = Query(
        None,
        description="Фильтр по кадастровому номеру"
        ),
    db: AsyncSession = Depends(get_db)
):
    """
    Возвращает историю всех запросов.
    Можно отфильтровать по кадастровому номеру.
    """
    if cadastral_number:
        history = await crud.get_history_by_cadastral(
            db,
            cadastral_number=cadastral_number
            )
    else:
        history = await crud.get_all_history(
            db,
            skip=0,
            limit=100
        )

    if not history:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Записи не найдены."
        )

    return history


@app.delete(
        "/history",
        summary="Удаление всей истории запросов",
        status_code=status.HTTP_204_NO_CONTENT
        )
async def clear_history(db: AsyncSession = Depends(get_db)) -> None:
    """Удаляет всю историю запросов."""
    await crud.delete_all_history(db=db)


@app.delete(
        "/history/{record_id}",
        summary="Удаление одной записи из истории",
        status_code=status.HTTP_204_NO_CONTENT
        )
async def delete_single_history(
    record_id: int,
    db: AsyncSession = Depends(get_db)
) -> None:
    """
    Удаляет одну конкретную запись из истории по её ID.
    """
    deleted_record = await crud.delete_history_record_by_id(
        db=db,
        record_id=record_id
    )
    if deleted_record is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Запись с ID {record_id} не найдена."
        )
