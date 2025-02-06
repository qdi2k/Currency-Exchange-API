import datetime

from pydantic import EmailStr
from sqlalchemy import BigInteger, DateTime, func, String
from sqlalchemy.orm import Mapped, mapped_column

from app.db.database import Base


class User(Base):
    """Модель пользователя."""

    __tablename__ = "users"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, index=True)
    email: Mapped[EmailStr] = mapped_column(
        String(255), unique=True, nullable=False
    )
    username: Mapped[str] = mapped_column(
        String(50), nullable=False
    )
    password: Mapped[str] = mapped_column(String(255), nullable=False)
    verified: Mapped[bool] = mapped_column(default=False, nullable=False)
    verification_token: Mapped[str] = mapped_column(
        String(255), nullable=True
    )
    data_register: Mapped[datetime.datetime] = mapped_column(
        DateTime, nullable=False, server_default=func.now()
    )
