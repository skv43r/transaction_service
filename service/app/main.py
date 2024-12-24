"""
Модуль для инициализации и настройки приложения FastAPI.
"""
from contextlib import asynccontextmanager
from fastapi import FastAPI
from app.database import engine
from app.routes import transaction
from common.models.base import Base
from common.logging_config import setup_logging

setup_logging()

app = FastAPI()

@asynccontextmanager
async def lifespan(app: FastAPI):
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

app.include_router(transaction.router, prefix="/transactions", tags=["Transactions"])