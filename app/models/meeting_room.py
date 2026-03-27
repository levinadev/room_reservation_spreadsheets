from sqlalchemy import String, Integer, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.db import Base, CommonMixin

class MeetingRoom(CommonMixin, Base):
    """
    Хранит информацию о переговорных комнатах.
    """
    name: Mapped[str] = mapped_column(
        String(100),
        unique=True,
        nullable=False,
        comment='Название переговорной комнаты',
    )
    description: Mapped[str] = mapped_column(
        String,
        nullable=True,
        comment='Описание комнаты',
    )
    reservations: Mapped[list['Reservation']] = relationship(cascade='delete')