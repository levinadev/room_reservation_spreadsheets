# app/core/db.py

# Импортируем тип поля Integer для создания столбца ID:
from sqlalchemy import Integer
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
# Импортируем Mapped и mapped_column - классы для описания столбцов таблицы:
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, declared_attr

from app.core.config import settings

class Base(DeclarativeBase):
    pass

class CommonMixin:

    @declared_attr
    def __tablename__(cls):
        # Имя таблицы будет создано из названия модели в нижнем регистре.
        return cls.__name__.lower()

    # Во все таблицы будет добавлено поле ID.
    id: Mapped[int] = mapped_column(Integer, primary_key=True)

engine = create_async_engine(settings.database_url)

AsyncSessionLocal = async_sessionmaker(engine, expire_on_commit=False)


# Асинхронный генератор сессий.
async def get_async_session():
    # При каждом вызове get_async_session()
    # из AsyncSessionLocal извлекается сессия и возвращается
    # тому, кто её запросил.
    async with AsyncSessionLocal() as async_session:
        yield async_session
        # Когда HTTP-запрос отработает - выполнение кода вернётся сюда;
        # контекстный менеджер завершит работу;
        # при завершении работы контекстного менеджера
        # сессия будет автоматически закрыта.