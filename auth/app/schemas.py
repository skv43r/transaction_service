"""
Модуль для определения схем данных с использованием Pydantic.
"""
from decimal import Decimal
from pydantic import BaseModel, EmailStr, Field, field_validator

class UserCreate(BaseModel):
    """
    Класс для создания нового пользователя.
    """
    username: str
    email: EmailStr
    password: str = Field(..., min_length=8)

    @field_validator("password")
    def validate_password(cls, value):
        """
        Проверяет, что новый пароль соответствует требованиям.

        Аргументы:
            cls: Класс, к которому относится валидатор.
            value: Значение пароля для проверки.

        Возвращает:
            Значение пароля, если он соответствует требованиям.

        Исключения:
            ValueError: Если пароль короче 8 символов.
        """
        if len(value) < 8:
            raise ValueError("Пароль должен быть длиннее 8 символов")
        return value

class UserLogin(BaseModel):
    """
    Класс для представления ответа пользователя.
    """
    username: str
    password: str = Field(..., min_length=8)

class UserResponse(BaseModel):
    """
    Класс для представления ответа пользователя.
    """
    id: int
    username: str
    email: EmailStr
    balance: Decimal

    class Config:
        """
        Конфигурация для модели UserResponse.
        """
        orm_mode = True

class Token(BaseModel):
    """
    Класс для получения токена.
    """
    access_token: str
    token_type: str = "bearer"

class PasswordChange(BaseModel):
    """
    Класс для изменения пароля пользователя.
    """
    username: str
    old_password: str
    new_password: str = Field(..., min_length=8)

    @field_validator("new_password")
    def validate_password(cls, value):
        """
        Проверяет, что новый пароль соответствует требованиям.

        Аргументы:
            cls: Класс, к которому относится валидатор.
            value: Значение пароля для проверки.

        Возвращает:
            Значение пароля, если он соответствует требованиям.

        Исключения:
            ValueError: Если пароль короче 8 символов.
        """
        if len(value) < 8:
            raise ValueError("Пароль должен быть длиннее 8 символов")
        return value
