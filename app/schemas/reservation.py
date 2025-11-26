# app/schemas/reservation.py
from typing import ClassVar
from pydantic import ConfigDict, Field, BaseModel, field_validator, model_validator
from datetime import datetime, timedelta
from typing_extensions import Self

class ReservationBase(BaseModel):
    # Константы с актуальной датой-временем, Pydantic не будет воспринимать как поля
    FROM_TIME: ClassVar[str] = (datetime.now() + timedelta(minutes=10)).isoformat(timespec='minutes')
    TO_TIME: ClassVar[str] = (datetime.now() + timedelta(hours=1)).isoformat(timespec='minutes')

    # Поля модели
    from_reserve: datetime = Field(..., examples=[FROM_TIME])
    to_reserve: datetime = Field(..., examples=[TO_TIME])


    model_config = ConfigDict(extra='forbid')


class ReservationCreate(ReservationBase):
    """
    Схема для полученных данных (создание объекта).
    
    редактировать можно только время бронирования, 
    а вот менять ID забронированной переговорки — нельзя. 
    Если пользователь захочет поменять забронированную переговорку 
    на другую — пусть удаляет старую бронь, а потом заводит новую;

    обновлять поля модели from_reserve и to_reserve можно только вместе.
    """
    meetingroom_id: int


class ReservationUpdate(ReservationBase):
    """
    Схема для полученных данных (обновление объекта).
    """
    @field_validator('from_reserve')
    @classmethod
    def check_from_reserve_later_than_now(cls, value):
        if value <= datetime.now():
            error = (
                'Время начала бронирования '
                'не может быть меньше текущего времени'
            )
            raise ValueError(error)
        return value

    @model_validator(mode='after')
    def check_from_reserve_before_to_reserve(self) -> Self:
        if self.from_reserve >= self.to_reserve:
            error = (
                'Время начала бронирования '
                'не может быть больше времени окончания'
            )
            raise ValueError(error)
        return self


class ReservationDB(BaseModel):
    """
    Схема для возвращаемого объекта.
    """
    id: int
    meetingroom_id: int
    user_id: int | None = None

    model_config = ConfigDict(from_attributes=True)