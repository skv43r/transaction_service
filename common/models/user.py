"""
Модуль для определения модели пользователя.
"""
from sqlalchemy import Column, Integer, String, DECIMAL
from .base import Base

class User(Base):
    """
    Класс для представления пользователя системы.
    """
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    email = Column(String, unique=True, index=True)
    balance = Column(DECIMAL, default=1000.0)
