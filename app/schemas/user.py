from fastapi_users import schemas

class UserRead(schemas.BaseUser[int]):
    """
    Схема для чтения объектов пользователя
    """

class UserCreate(schemas.BaseUserCreate):
    """
    Схема для создания объектов пользователя
    """

class UserUpdate(schemas.BaseUserUpdate):
    """
    Схема для обновления объектов пользователя
    """
