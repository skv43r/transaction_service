"""
Модуль для аутентификации пользователей.
"""
from typing import List
import logging
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app import schemas
from app.utils import create_access_token, hash_password, verify_password, get_db
from common.models.user import User

logger = logging.getLogger(__name__)

router = APIRouter()

@router.post("/register", response_model=schemas.UserResponse)
async def register(user: schemas.UserCreate,
                   db: AsyncSession = Depends(get_db)) -> schemas.UserResponse:
    """
    Регистрация нового пользователя.

    - Параметры:
        - `user`: Объект, содержащий имя пользователя, email и пароль.

    - Ответ:
        - Возвращает информацию о зарегистрированном пользователе.

    - Ошибки:
        - 400: Если имя пользователя или email уже заняты.
    """
    logger.info("Попытка регистрации пользователя: %s", user.username)
    result = await db.execute(
        select(User).filter(User.username == user.username)
    )
    existing_user = result.scalar_one_or_none()
    if existing_user:
        logger.warning("Имя пользователя уже занято: %s", user.username)
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail="Имя уже занято")

    result = await db.execute(
        select(User).filter(User.email == user.email)
    )
    existing_email = result.scalar_one_or_none()
    if existing_email:
        logger.warning("Email уже используется: %s", user.email)
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail="Email уже используется")

    hashed_password = hash_password(user.password)

    new_user = User(
        username = user.username,
        email = user.email,
        hashed_password = hashed_password,
        balance=1000.0
    )

    db.add(new_user)
    await db.commit()
    await db.refresh(new_user)
    logger.info("Пользователь зарегистрирован: %s", user.username)
    return new_user

@router.post("/login", response_model=schemas.Token)
async def login(user: schemas.UserLogin,
                db: AsyncSession = Depends(get_db)) -> schemas.Token:
    """
    Вход пользователя в систему.

    - Параметры:
        - `user`: Объект, содержащий имя пользователя и пароль.

    - Ответ:
        - Возвращает токен доступа и тип токена.

    - Ошибки:
        - 401: Если имя пользователя или пароль неверны.
    """
    logger.info("Попытка входа пользователя: %s", user.username)
    async with db.begin():
        result = await db.execute(
            select(User).filter(User.username == user.username)
        )
        db_user = result.scalar_one_or_none()
        if not db_user or not verify_password(user.password, db_user.hashed_password):
            logger.warning("Неверное имя пользователя или пароль: %s", user.username)
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                                detail="Неверное имя пользователя или пароль")

        token = create_access_token({"sub": db_user.username})
        logger.info("Пользователь успешно вошел: %s", user.username)
        return {"access_token": token, "token_type": "bearer"}

@router.put("/change-password", response_model=schemas.UserResponse)
async def change_password(
    data: schemas.PasswordChange,
    db: AsyncSession = Depends(get_db)) -> schemas.UserResponse:
    """
    Изменение пароля пользователя.

    - Параметры:
        - `data`: Объект, содержащий имя пользователя, старый и новый пароли.

    - Ответ:
        - Возвращает информацию о пользователе с обновленным паролем.

    - Ошибки:
        - 400: Если неверное имя пользователя, старый пароль или новый пароль 
        слишком короткий (менее 8 символов).
    """
    logger.info("Попытка смены пароля пользователя: %s", data.username)
    result = await db.execute(
        select(User).filter(User.username == data.username)
    )
    db_user = result.scalar_one_or_none()
    if not db_user or not verify_password(data.old_password, db_user.hashed_password):
        logger.warning("Неверное имя пользователя или старый пароль: %s", data.username)
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail="Неверное имя пользователя или пароль")

    if len(data.new_password) < 8:
        logger.warning("Новый пароль слишком короткий для пользователя: %s", data.username)
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Новый пароль должен быть длиннее 8 символов"
        )

    db_user.hashed_password = hash_password(data.new_password)
    db.add(db_user)
    await db.commit()
    await db.refresh(db_user)
    logger.info("Пароль пользователя изменен: %s", data.username)
    return db_user

@router.get("/users", response_model=list[schemas.UserResponse])
async def get_all_users(skip: int = 0, limit: int = 10,
                        db: AsyncSession = Depends(get_db)) -> List[schemas.UserResponse]:
    """
    Получение списка всех пользователей.

    - Параметры:
        - `skip`: Количество пропускаемых пользователей (по умолчанию 0).
        - `limit`: Максимальное количество возвращаемых пользователей (по умолчанию 10).

    - Ответ:
        - Возвращает список пользователей.

    - Ошибки:
        - 200: Если пользователи найдены.
    """
    logger.info("Получение списка пользователей: skip=%d, limit=%d", skip, limit)
    result = await db.execute(select(User).offset(skip).limit(limit=limit))
    users = result.scalars().all()
    logger.info("Найдено пользователей: %d", len(users))
    return users

@router.get("/users/{user_id}", response_model=schemas.UserResponse)
async def get_user(user_id: int,
                   db: AsyncSession = Depends(get_db)) -> schemas.UserResponse:
    """
    Получение информации о пользователе по его ID.

    - Параметры:
        - `user_id`: ID пользователя.

    - Ответ:
        - Возвращает информацию о пользователе.

    - Ошибки:
        - 404: Если пользователь с указанным ID не найден.
    """
    logger.info("Получение данных пользователя с ID: %d", user_id)
    result = await db.execute(select(User).filter(User.id == user_id))
    user = result.scalar_one_or_none()
    if not user:
        logger.warning("Пользователь с ID %d не найден", user_id)
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail="Пользователь не найден")
    logger.info("Пользователь с ID %d найден", user_id)
    return user
