"""
Модуль для определения схем данных с использованием Pydantic.
"""
from typing import Optional
from datetime import datetime
from decimal import Decimal
from enum import Enum
from pydantic import BaseModel

class TransactionStatus(str, Enum):
    """
    Класс для статусов транзакций.
    """
    PENDING = "pending"
    COMPLETED = "completed"
    FAILED = "failed"

class TransactionCreate(BaseModel):
    """
    Класс для создания транзакции.
    """
    receiver_id: int
    amount: Decimal

class TransactionResponse(BaseModel):
    """
    Класс для представления ответа на запрос о транзакции.
    """
    id: int
    sender_id: int
    receiver_id: int
    amount: Decimal
    status: TransactionStatus
    created_at: datetime

    class Config:
        """
        Конфигурация для модели UserResponse.
        """
        orm_mode = True

class TransactionFilter(BaseModel):
    """
    Класс для фильтрации транзакций.
    """
    start_date: Optional[datetime]
    end_date: Optional[datetime]
    status: Optional[TransactionStatus]
