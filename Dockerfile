FROM python:3.12-slim

WORKDIR /app

COPY pyproject.toml .
RUN pip install --no-cache-dir \
    aiogoogle==5.13.0 \
    aiosqlite==0.20.0 \
    alembic==1.13.1 \
    fastapi==0.115.5 \
    fastapi-users[sqlalchemy]==13.0.0 \
    pydantic-settings==2.6.1 \
    sqlalchemy[asyncio]==2.0.30 \
    uvicorn[standard]==0.32.1

COPY . .

CMD ["sh", "-c", "alembic upgrade head && uvicorn app.main:app --host 0.0.0.0 --port 8000"]
