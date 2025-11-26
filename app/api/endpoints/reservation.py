# app/api/endpoints/reservaion.py
from typing import Annotated

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.validators import (
    check_meeting_room_exists, check_reservation_intersections,
    check_reservation_before_edit
)
from app.core.db import get_async_session
from app.crud.reservation import reservation_crud
from app.schemas.reservation import ReservationCreate, ReservationDB, ReservationUpdate
from app.models import User
from app.core.user import current_superuser, current_user

router = APIRouter()
SessionDep = Annotated[AsyncSession, Depends(get_async_session)]


@router.post('/', response_model=ReservationDB)
async def create_reservation(
        reservation: ReservationCreate,
        session: SessionDep,
        user: Annotated[User, Depends(current_user)],
):
    """
    Резервирование переговорки и привязка к пользователю
    """
    await check_meeting_room_exists(
        reservation.meetingroom_id, session
    )
    await check_reservation_intersections(
        # Так как валидатор принимает **kwargs,
        # аргументы должны быть переданы с указанием ключей.
        **reservation.model_dump(), session=session
    )
    new_reservation = await reservation_crud.create(
        reservation, session, user
    )
    return new_reservation


@router.get(
    '/',
    response_model=list[ReservationDB],
    dependencies=[Depends(current_superuser)],
)
async def get_all_reservations(
        session: SessionDep
):
    """
    Роутер для получения списка всех бронирований.
    Только для суперюзеров.
    """
    reservations = await reservation_crud.get_multi(session)
    return reservations


@router.get(
    '/my_reservations',
    response_model=list[ReservationDB],
    # Добавляем множество с полями, которые надо исключить из ответа.
    response_model_exclude={'user_id'},
)
async def get_my_reservations(
    session: SessionDep,
    # Передаём зависимость в аргументы функции, а не декоратора.
    # В этой зависимости получаем обычного пользователя, а не суперюзера.
    user: Annotated[User, Depends(current_user)]
):
    """
    Роутер для получения всех
    бронирований текущего пользователяя
    """
    reservations = await reservation_crud.get_by_user(
        session=session,
        user=user
    )
    return reservations


@router.delete('/{reservation_id}', response_model=ReservationDB)
async def delete_reservation(
        reservation_id: int,
        session: SessionDep,
        # Новая зависимость.
        user: Annotated[User, Depends(current_user)],
):
    """
    Роутер для удаления данных.

    :param reservation_id:
    :param session:
    :return:
    """
    reservation = await check_reservation_before_edit(
        reservation_id, session, user
    )
    reservation = await reservation_crud.remove(
        reservation, session
    )
    return reservation


@router.patch('/{reservation_id}', response_model=ReservationDB)
async def update_reservation(
        reservation_id: int,
        obj_in: ReservationUpdate,
        session: SessionDep,
        # Новая зависимость.
        user: Annotated[User, Depends(current_user)],
):
    # Проверяем, что запрошенный объект бронирования существует.
    reservation = await check_reservation_before_edit(
        reservation_id, session, user
    )
    # Проверяем, что нет пересечений с другими бронированиями.
    await check_reservation_intersections(
        # Новое время бронирования, распакованное на ключевые аргументы.
        **obj_in.model_dump(),
        # id обновляемого объекта бронирования:
        reservation_id=reservation_id,
        # id переговорки:
        meetingroom_id=reservation.meetingroom_id,
        session=session
    )
    reservation = await reservation_crud.update(
        db_obj=reservation,
        # На обновление передаём объект класса ReservationUpdate.
        obj_in=obj_in,
        session=session,
    )
    return reservation
