from pathlib import Path

from pydantic import Field
from pydantic_settings import BaseSettings


BASE_DIR = Path(__file__).resolve().parent.parent
API_TITLE = """API currency convert"""
API_VERSION = "0.0.1"
API_DESCRIPTION = """
    API проект для обмена валют. Пользователи могут получать последние курсы
    обмена различных валют и выполнять конвертацию валют. Проект включает в 
    себя аутентификацию JWT для доступа пользователей и интеграцию с открытым 
    API обменных курсов для получения данных об обменных курсах в режиме 
    реального времени.
""".strip()


class Settings(BaseSettings):
    """
    Базовые настройки проекта. Выполняет инициализацию параметров из
    переменных окружения.
    """
    DEBUG: bool = Field(default=False, description="True or False")
    ALLOWED_HOSTS: str = Field(default="localhost 127.0.0.1")

    SCHEME: str = 'postgresql+asyncpg'

    DB_USER: str = Field(description='Database username')
    DB_PASS: str = Field(description='Database password')
    DB_HOST: str = Field(description='Database host')
    DB_PORT: str = Field(description='Database port')
    DB_NAME: str = Field(description='Database name')

    CURRENCY_DATA_API: str

    SECRET_KEY: str
    ALGORITHM: str
    ACCESS_TOKEN_EXPIRE_MINUTES: int

    @property
    def get_async_database_url(self) -> str:
        """Получение URL-адреса для асинхронного подключения к Postgres"""
        return (
            f"postgresql+asyncpg://{self.DB_USER}:{self.DB_PASS}"
            + f"@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"
        )

    class Config:
        env_file = '.env'
        env_file_encoding = 'utf-8'


settings = Settings()
