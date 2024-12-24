"""
Утилиты для работы с аутентификацией и хешированием паролей.
"""
from datetime import datetime, timedelta
from passlib.context import CryptContext
import jwt
from app.database import AsyncSessionLocal
from app.config import settings

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

async def get_db():
    """
    Асинхронный генератор для получения сессии базы данных.

    Этот генератор создает новую сессию базы данных и автоматически закрывает ее
    после завершения работы.

    Возвращает:
    - AsyncSession: Асинхронная сессия базы данных.
    """
    async with AsyncSessionLocal() as session:
        yield session

def hash_password(password: str) -> str:
    """
    Хеширование пароля.

    Принимает пароль в виде строки и возвращает его хешированное значение.

    Параметры:
    - password (str): Пароль, который необходимо хешировать.

    Возвращает:
    - str: Хешированный пароль.
    """
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Проверка пароля.

    Сравнивает введенный пароль с хешированным значением.

    Параметры:
    - plain_password (str): Введенный пароль.
    - hashed_password (str): Хешированный пароль.

    Возвращает:
    - bool: True, если пароли совпадают, иначе False.
    """
    return pwd_context.verify(plain_password, hashed_password)

def create_access_token(data: dict) -> str:
    """
    Создание токена доступа.

    Принимает данные, добавляет к ним время истечения и возвращает закодированный JWT.

    Параметры:
    - data (dict): Данные, которые необходимо закодировать в токен.

    Возвращает:
    - str: Закодированный JWT.
    """
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(seconds=settings.JWT_EXPIRATION)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode,
                             settings.JWT_SECRET,
                             algorithm=settings.JWT_ALGORITHM)
    return encoded_jwt
