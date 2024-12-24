"""
Модуль конфигурации для приложения аутентификации.
"""
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    """
    Класс для хранения настроек приложения аутентификации.
    """
    DATABASE_URL: str
    JWT_SECRET: str
    JWT_ALGORITHM: str = "HS256"
    JWT_EXPIRATION: int = 3600

    class Config:
        """
        Конфигурация для класса Settings.
        """
        env_file = ".env"

settings = Settings()
