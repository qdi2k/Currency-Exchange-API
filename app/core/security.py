from datetime import datetime, timedelta, timezone
from typing import Dict, Any, Optional, Annotated

import jwt
from fastapi import Depends, HTTPException
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from itsdangerous import (URLSafeTimedSerializer, BadSignature,
                          SignatureExpired)
from jwt import PyJWTError
from passlib.context import CryptContext
from starlette import status

from app.api.schemas.user import TokenData
from app.core.config import settings
from app.core.exception import (credentials_token_err,
                                credentials_not_token_exception)

security = HTTPBearer(auto_error=False)
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


async def get_current_user(
        credentials: Annotated[
            HTTPAuthorizationCredentials, Depends(security)
        ]
) -> TokenData:
    """
    Зависимость, которая проверяет JWT-токен и возвращает его полезную
    нагрузку. Если токен невалиден, выбрасывает исключение 401.
    """
    if not credentials:
        raise credentials_not_token_exception
    if not credentials or credentials.scheme != "Bearer":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Неверный формат токена"
        )

    token = credentials.credentials
    payload = await decode_access_token(token=token)
    try:
        if not payload:
            raise credentials_token_err
        email, user_id = payload.get("email"), payload.get("user_id")
        if email is None or user_id is None:
            raise credentials_token_err
    except PyJWTError:
        raise credentials_token_err

    return TokenData(email=email, user_id=user_id)
