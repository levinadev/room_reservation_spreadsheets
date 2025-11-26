# app/models/reservation.py
from datetime import datetime

from sqlalchemy import String, DateTime, Integer, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column

from app.core.db import Base, CommonMixin


class Reservation(CommonMixin, Base):
    """
    Управляет бронированием помещений.
    Объекты этой модели будут хранить информацию о том,
    на какие интервалы времени забронированы переговорки, описанные в MeetingRoom.
    """
    from_reserve: Mapped[datetime] = mapped_column(
        DateTime,
        comment='Время, с которого начинается бронирование',
    )
    to_reserve: Mapped[datetime] = mapped_column(
        DateTime,
        comment='Время, до которого забронирована переговорка',
    )
    # Столбец с внешним ключом: ссылка на таблицу meetingroom.
    # Имя поля в классе ForeignKey указывается в кавычках,
    # в формате название_таблицы.название_поля:
    meetingroom_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey('meetingroom.id'),
        comment='Внешний ключ к столбцу id таблицы meetingroom',
    )
    # Добавляем новое поле, ссылающееся на id пользователя; тип поля - внешний ключ.
    user_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey('user.id', name='fk_reservation_user_id_user'),
        nullable=True
    )

    def __repr__(self):
        return (
            f'Забронировано с {self.from_reserve} по {self.to_reserve}'
        )
