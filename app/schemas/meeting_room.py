from pydantic import ConfigDict, Field, BaseModel, field_validator

class MeetingRoomBase(BaseModel):
    name: str | None = Field(None, min_length=1, max_length=100)
    description: str | None = None


class MeetingRoomCreate(MeetingRoomBase):
    """
    Описывает объект переговорки отправляемый в БД.
    Попадают данные ещё не сохранённой переговорки.
    """
    name: str = Field(..., min_length=1, max_length=100) # ... - это обязателньое поле


class MeetingRoomDB(MeetingRoomBase):
    """
    Описывает объект переговорки, полученный из БД
    """
    id: int = Field(..., gt=0)

    model_config = ConfigDict(from_attributes=True)

class MeetingRoomUpdate(MeetingRoomBase):
    """
    Описывает объект для обновления данных.
    """
    @field_validator('name')
    @classmethod
    def name_cannot_be_null(cls, value):
        if value is None:
            raise ValueError('Имя переговорки не может быть пустым!')
        return value

