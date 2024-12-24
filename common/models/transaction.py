"""
Модуль для определения модели транзакций.
"""
from datetime import datetime
from sqlalchemy import Column, Integer, DECIMAL, String, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from .base import Base

class Transaction(Base):
    """
    Класс для представления транзакции между пользователями.
    """
    __tablename__ = "transactions"

    id = Column(Integer, primary_key=True, index=True)
    sender_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    receiver_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    amount = Column(DECIMAL, nullable=False)
    status = Column(String, default="pending")
    created_at = Column(DateTime, default=datetime.utcnow)

    sender = relationship("User", foreign_keys=[sender_id])
    receiver = relationship("User", foreign_keys=[receiver_id])
