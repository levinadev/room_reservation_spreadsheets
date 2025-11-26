# app/main.py
from fastapi import FastAPI

# Импортируем главный роутер.
from app.api.routers import main_router
from app.core.config import settings

# Создаётся объект приложения:
app = FastAPI(
    title=settings.app_title,
    description=settings.app_description,
)

# Подключаем главный роутер к объекту приложения:
app.include_router(main_router)
