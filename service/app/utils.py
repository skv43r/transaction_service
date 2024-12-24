"""
Утилиты для работы с аутентификацией и обработкой токенов.
"""
from datetime import datetime
import jwt
from fastapi import Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.database import AsyncSessionLocal
from app.config import settings
from common.models.user import User

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

async def get_current_user(token: str, db: AsyncSession = Depends(get_db)) -> User:
    """
    Получение текущего пользователя на основе токена JWT.

    Декодирует токен, проверяет его действительность и извлекает информацию о пользователе.
    Если токен недействителен или пользователь не найден, выбрасывает соответствующее исключение.

    Параметры:
    - token (str): JWT токен, содержащий информацию о пользователе.
    - db (AsyncSession): Сессия базы данных, полученная через зависимость.

    Возвращает:
    - User: Объект пользователя, если токен действителен и пользователь найден.

    Исключения:
    - HTTPException: Если токен недействителен, истек или пользователь не найден.
    """
    try:
        payload = jwt.decode(token, settings.JWT_SECRET,
                             algorithms=settings.JWT_ALGORITHM)
        username = payload.get("sub")
        exp_timestamp = payload.get("exp")

        if username is None:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                                detail="Неверный токен")

        if exp_timestamp and datetime.utcfromtimestamp(exp_timestamp) < datetime.utcnow():
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                                detail="Токен истек")
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail="Токен истек")
    except jwt.PyJWTError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail="Неверный токен")

    result = await db.execute(select(User).filter(User.username == username))
    user = result.scalar_one_or_none()

    if user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail="Пользователь не найден")

    return user
