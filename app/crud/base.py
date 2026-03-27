from fastapi.encoders import jsonable_encoder
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.models import User

class CRUDBase:

    def __init__(self, model):
        self.model = model

    async def get(
        self,
        obj_id: int,
        session: AsyncSession,
    ):
        """
        Универсальный метод для получения объекта по его id

        :param obj_id:
        :param session:
        :return:
        """
        db_obj = await session.execute(
            select(self.model).where(
                self.model.id == obj_id
            )
        )
        return db_obj.scalars().first()

    async def get_multi(
        self,
        session: AsyncSession
    ):
        """
        Универсальный метод для получения всех объектов заданной модели:

        :param session:
        :return:
        """
        db_objs = await session.execute(select(self.model))
        return db_objs.scalars().all()

    async def create(
        self,
        obj_in,
        session: AsyncSession,
        user: User | User = None,
    ):
        """
        Создаём запись в БД по данным из Pydantic-схемы.
        :param obj_in: Данные из схемы
        :param session:
        :return: Созданный объект
        """
        obj_in_data = obj_in.model_dump()

        if user is not None:
            obj_in_data['user_id'] = user.id

        db_obj = self.model(**obj_in_data)
        session.add(db_obj)
        await session.commit()
        await session.refresh(db_obj)
        return db_obj

    async def update(
        self,
        db_obj,
        obj_in,
        session: AsyncSession,
    ):
        """
        Функция должна обновить значения полей объекта,
        полученного из БД, и возвращать этот объект.

        :param db_obj: Объект из БД для обновления
        :param obj_in: Объект из запроса
        :param session: Сессия
        :return: Обновленный объект
        """
        obj_data = jsonable_encoder(db_obj)
        update_data = obj_in.dict(exclude_unset=True)

        for field in obj_data:
            if field in update_data:
                setattr(db_obj, field, update_data[field])
        session.add(db_obj)
        await session.commit()
        await session.refresh(db_obj)
        return db_obj

    async def remove(
        self,
        db_obj,
        session: AsyncSession,
    ):
        """
        Удаление объекта из БД.
        :param db_obj:
        :param session:
        :return:
        """
        await session.delete(db_obj)
        await session.commit()
        return db_obj