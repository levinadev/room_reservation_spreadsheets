# app/api/meeting_room.py
from typing import Annotated

from fastapi import APIRouter, HTTPException, Depends

from sqlalchemy.ext.asyncio import AsyncSession

from app.api.validators import check_name_duplicate, check_meeting_room_exists
from app.crud.meeting_room import meeting_room_crud
from app.crud.reservation import reservation_crud

from app.models.meeting_room import MeetingRoom
from app.schemas.meeting_room import (
    MeetingRoomCreate,
    MeetingRoomDB, MeetingRoomUpdate
)
from app.core.db import get_async_session
from app.schemas.reservation import ReservationDB
# Добавьте импорт зависимости, определяющей,
# что текущий пользователь - суперюзер.
from app.core.user import current_superuser

router = APIRouter()

SessionDep = Annotated[AsyncSession, Depends(get_async_session)]


@router.post(
    '/',
    # Указываем, что функция должна вернуть объект типа MeetingRoomDB.
    response_model=MeetingRoomDB,
    response_model_exclude_none=True,
    # Добавьте вызов зависимости при обработке запроса.
    dependencies=[Depends(current_superuser)],
)
async def create_new_meeting_room(
        meeting_room: MeetingRoomCreate,
        session: SessionDep,
):
    """
    Роутер для добавления данных. Только для суперюзеров.
    """
    # Вызываем функцию проверки уникальности поля name:
    await check_name_duplicate(meeting_room.name, session)
    new_room = await meeting_room_crud.create(meeting_room, session)
    return new_room


@router.get(
    '/',
    response_model=list[MeetingRoomDB],
    response_model_exclude_none=True,
)
async def get_all_meeting_rooms(
        session: SessionDep,
):
    """
    Роутер для получения всех переговорныхз комнат.
    """
    all_rooms = await meeting_room_crud.get_multi(session)
    return all_rooms


@router.patch(
    '/{meeting_room_id}',
    response_model=MeetingRoomDB,
    dependencies=[Depends(current_superuser)],
)
async def partially_update_meeting_room(
        meeting_room_id: int,
        obj_in: MeetingRoomUpdate,
        session: SessionDep,
):
    """
    Роутер для обновления переговорки. Только для суперюзеров."
    """
    # Вызываем check_meeting_room_exists(): пытаемся получить по id объект из БД.
    # В ответ ожидаем либо None, либо объект класса MeetingRoom.
    meeting_room = await check_meeting_room_exists(
        meeting_room_id,
        session
    )
    if obj_in.name is not None:
        # Если в запросе получено поле name — проверяем его на уникальность.
        await check_name_duplicate(obj_in.name, session)

    # Передаём в корутину все данные, необходимые для обновления объекта.
    meeting_room = await meeting_room_crud.update(
        meeting_room, obj_in, session
    )
    return meeting_room


@router.delete(
    '/{meeting_room_id}',
    response_model=MeetingRoomDB,
    response_model_exclude_none=True,
    dependencies=[Depends(current_superuser)],
)
async def remove_meeting_room(
        meeting_room_id: int,
        session: SessionDep,
):
    """
    Роутер для удаления данных. Только для суперюзеров.
    """
    # Вызываем корутину, проверяющую существование запрошенного объекта.
    meeting_room = await check_meeting_room_exists(
        meeting_room_id, session
    )
    meeting_room = await meeting_room_crud.remove(
        meeting_room, session
    )
    return meeting_room


@router.get(
    '/{meeting_room_id}/reservations',
    response_model=list[ReservationDB],
    # Добавляем множество с полями, которые надо исключить из ответа.
    response_model_exclude={'user_id'},
)
async def get_reservations_for_room(
        meeting_room_id: int,
        session: SessionDep,
):
    """
    Роутер, который выводит занятые интервалы для комнаты(переданный id).
    """
    await check_meeting_room_exists(meeting_room_id, session)
    reservations = await reservation_crud.get_future_reservations_for_room(
        room_id=meeting_room_id, session=session
    )
    return reservations