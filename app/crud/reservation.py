# app/crud/reservation.py
"""
Готово! Теперь в файле с эндпоинтами можно использовать методы объекта reservation_crud.
Если для какой-то модели нужны уникальные методы, которых нет в базовом классе
— создаём класс-наследник базового класса,
добавляем в него нужный метод — и создаём объект уже на основе этого нового класса.
"""
from datetime import datetime

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.sql.elements import and_

from app.crud.base import CRUDBase
from app.models import Reservation, User
# reservation_crud = CRUDBase(Reservation)


class CRUDReservation(CRUDBase):

    async def get_reservations_at_the_same_time(
            self,
            from_reserve: datetime,
            to_reserve: datetime,
            meetingroom_id: int,
            session: AsyncSession,
            reservation_id: int | None = None,
    ) -> list[Reservation]:
        """
        Запрос к базе данных, который вернёт для конкретной переговорки
        все объекты Reservation, пересекающиеся по
        времени с запрошенным временем бронирования.

        :param from_reserve:
        :param to_reserve:
        :param meetingroom_id:
        :param session:
        :param reservation_id: id объекта бронирования (при обновлении).
        :return:
        """
        # Выносим существующий запрос к БД в отдельное выражение.
        statement = select(Reservation).where(
            Reservation.meetingroom_id == meetingroom_id,
            and_(
                from_reserve <= Reservation.to_reserve,
                to_reserve >= Reservation.from_reserve
            )
        )
        # Если передан id бронирования...
        if reservation_id is not None:
            # ... то к выражению нужно добавить новое условие.
            statement = statement.where(
                # id искомых объектов не должны быть равны id обновляемого объекта.
                Reservation.id != reservation_id
            )
        # Выполняем запрос.
        reservations = await session.execute(statement)
        reservations = reservations.scalars().all()
        return reservations


    async def get_future_reservations_for_room(
            self,
            room_id: int,
            session: AsyncSession,
    ):
        """
        Возвращает объекты бронирования, связанные с конкретной переговоркой.

        :param room_id:
        :param session:
        :return:
        """
        reservations = await session.execute(
            # Получить все объекты Reservation...
            select(Reservation).where(
                # ...где внешний ключ meetingroom_id
                # равен id запрашиваемой переговорки...
                Reservation.meetingroom_id == room_id,
                # ...а время конца бронирования больше текущего времени.
                Reservation.to_reserve > datetime.now()
            )
        )
        reservations = reservations.scalars().all()
        return reservations

    async def get_by_user(
            self,
            user: User,
            session: AsyncSession,
    ):
        """
        Возвращать список объектов модели Reservation, связанных с пользователем, отправившим запрос.

        :return:
        """
        db_objs = await session.execute(
            select(Reservation).where(
                Reservation.user_id == user.id
            )
        )
        return db_objs.scalars().all()


reservation_crud = CRUDReservation(Reservation)