from pathlib import Path

from fastapi_mail import ConnectionConfig
from pydantic import Field, EmailStr, SecretStr
from pydantic_settings import BaseSettings


BASE_DIR = Path(__file__).resolve().parent.parent
API_TITLE = """API currency convert"""
API_VERSION = "0.0.1"
API_DESCRIPTION = """
    API проект для обмена валют. Проект предоставляет пользователям возможность 
    получать актуальные курсы обмена валют в режиме реального времени и 
    выполнять конвертацию между различными валютами. 
    Функциональные конечные точки защищены, доступ к ним
    предоставляется после безопасной регистрации пользователей с подтверждением
    электронной почты через SMTP и надежной аутентификацией с использованием 
    JWT. 
""".strip()


class Settings(BaseSettings):
    """
    Базовые настройки проекта. Выполняет инициализацию параметров из
    переменных окружения.
    """
    # Настройки FastAPI
    DEBUG: bool = Field(default=False, description="True or False")
    ALLOWED_HOSTS: str = Field(default="localhost 127.0.0.1")
    SECRET_KEY: str = Field(description='Secret key')

    # Подключение к БД
    DB_USER: str = Field(description='Database username')
    DB_PASS: str = Field(description='Database password')
    DB_HOST: str = Field(description='Database host')
    DB_PORT: str = Field(description='Database port')
    DB_NAME: str = Field(description='Database name')

    # Токен APILayer
    CURRENCY_DATA_API: str = Field(description='TOKEN APILAYER')

    # Настройки JWT
    ALGORITHM: str = Field(description='JWT crypto algorithm')
    ACCESS_TOKEN_EXPIRE_MINUTES: int = Field(description='JWT time-life')

    # Настройки почтового агента
    SMTP_USER: EmailStr = Field(description="Email username")
    SMTP_PASSWORD: SecretStr = Field(description="Email password")
    SMTP_HOST: str = Field(description="Email host")
    SMTP_PORT: int = Field(description="Email port")
    SMTP_SSL_TLS: bool = Field(
        default=True, description="Email use SSL or TSL - True or False"
    )
    MAIL_STARTTLS: bool = False
    MAIL_USE_CREDENTIALS: bool = True
    MAIL_VALIDATE_CERTS: bool = True
    MAIL_CONF: ConnectionConfig | None = None

    def __init__(self, **data):
        super().__init__(**data)
        self.MAIL_CONF = self.get_connect_email_sender()

    @property
    def get_async_database_url(self) -> str:
        """Получение URL-адреса для асинхронного подключения к Postgres"""
        return (
            f"postgresql+asyncpg://{self.DB_USER}:{self.DB_PASS}"
            + f"@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"
        )

    def get_connect_email_sender(self):
        """
        Использует параметры, заданные в классе Settings, для создания
        объекта ConnectionConfig, который определяет настройки подключения к
        почтовому серверу.
        """
        return ConnectionConfig(
            MAIL_USERNAME=str(self.SMTP_USER),
            MAIL_PASSWORD=self.SMTP_PASSWORD,
            MAIL_FROM=self.SMTP_USER,
            MAIL_PORT=int(self.SMTP_PORT),
            MAIL_SERVER=self.SMTP_HOST,
            MAIL_STARTTLS=self.MAIL_STARTTLS,
            MAIL_SSL_TLS=self.SMTP_SSL_TLS,
            USE_CREDENTIALS=self.MAIL_USE_CREDENTIALS,
            VALIDATE_CERTS=self.MAIL_VALIDATE_CERTS
        )

    class Config:
        env_file = '.env'
        env_file_encoding = 'utf-8'


settings = Settings()
