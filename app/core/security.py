from datetime import datetime, timedelta, timezone
from typing import Dict, Any, Optional

import jwt
from itsdangerous import (URLSafeTimedSerializer, BadSignature,
                          SignatureExpired)
from passlib.context import CryptContext

from app.core.config import settings

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def get_password_hash(password: str) -> str:
    """
    Хэширует пароль с использованием bcrypt.
    """
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Проверяет, соответствует ли пароль его хэшу.
    """
    return pwd_context.verify(plain_password, hashed_password)


def generate_verification_token(user_id: int) -> str:
    """
    Генерация токена для подтверждения email.
    """
    serializer = URLSafeTimedSerializer(settings.SECRET_KEY)
    return serializer.dumps(user_id)


def verify_verification_token(
        token: str, max_age: int = 3600
    ) -> Optional[int]:
    """
    Проверка токена для подтверждения email.
    """
    serializer = URLSafeTimedSerializer(settings.SECRET_KEY)
    try:
        user_id = serializer.loads(token, max_age=max_age)
        return user_id
    except BadSignature or SignatureExpired:
        return None


async def create_access_token(data: Dict[str, Any]) -> str:
    """
    Создает JWT-токен и добавляет к нему полезную нагрузку
    """
    access_token_expires = timedelta(
        minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
    )
    to_encode = data.copy()
    to_encode.update(
        {"exp": datetime.now(timezone.utc) + access_token_expires}
    )
    return jwt.encode(
        payload=to_encode, key=settings.SECRET_KEY,
        algorithm=settings.ALGORITHM
    )


async def decode_access_token(token: str) -> Optional[Dict[str, Any]]:
    """
    Декодирует JWT-токен, возвращая его полезную нагрузку
    """
    try:
        return jwt.decode(
            jwt=token, key=settings.SECRET_KEY,
            algorithms=[settings.ALGORITHM]
        )
    except jwt.PyJWTError:
        return None
