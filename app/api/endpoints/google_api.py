from datetime import datetime
from aiogoogle import Aiogoogle
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.db import get_async_session
from app.core.google_client import get_service
from app.core.user import current_superuser

from app.crud.reservation import reservation_crud
from app.services.google_api import update_spreadsheets_value

router = APIRouter()

@router.post(
    '/',
    response_model=list[dict[str, int]],
    dependencies=[Depends(current_superuser)],
)
async def get_report(
        from_reserve: datetime,
        to_reserve: datetime,
        session: AsyncSession = Depends(get_async_session),
        wrapper_services: Aiogoogle = Depends(get_service)
):
    """
    Получение данных о том сколько раз за указанный
    период была забронирована каждая переговорка.

    Только для суперюзеров.
    """
    reservations = await reservation_crud.get_count_res_at_the_same_time(
        from_reserve, to_reserve, session
    )

    SPREADSHEET_ID = "1zlOpNuqh0-M7C1lms4kliXNEhOzCxmb83Rc1XGte0KI"

    await update_spreadsheets_value(
        SPREADSHEET_ID,
        reservations,
        wrapper_services
    )

    return reservations