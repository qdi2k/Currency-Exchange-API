from typing import Optional, Dict, Any

from fastapi import HTTPException
from pydantic import EmailStr
from starlette import status

from app.api.schemas.auth import (RequestUserCreate, ResponseUserCreate,
                                  RequestUserLogin, ResponseUserLogin,
                                  AllUserData)
from app.core.security import (get_password_hash, verify_password,
                               create_access_token)
from app.db.models import User
from app.utils.unitofwork import IUnitOfWork


class AuthUserService:
    """
    Бизнес логика работы с пользователями
    """

    def __init__(self, uow: IUnitOfWork):
        self.uow = uow

    async def registration(
            self, user_data: RequestUserCreate
    ) -> ResponseUserCreate:
        """
        Регистрация пользователя
        """
        if await self.find_user_by_email(user_email=user_data.email):
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Пользователь с таким Email уже существует"
            )

        user_data.password = get_password_hash(password=user_data.password)
        user_dict: Dict[str, Any] = user_data.model_dump()

        async with self.uow:
            user_from_db = await self.uow.user.add_one(user_dict)
            user_to_return = ResponseUserCreate.model_validate({
                "id": user_from_db.id,
                "email": user_from_db.email,
                "username": user_from_db.username,
                "data_register": user_from_db.data_register,
            })
            await self.uow.commit()
            return user_to_return

    async def login(
            self, user_data: RequestUserLogin
    ) -> ResponseUserLogin:
        """
        Вход пользователя в систему
        """
        user = await self.find_user_by_email(user_email=user_data.email)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Пользователь с таким Email не найден"
            )
        if not verify_password(user_data.password, user.password):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Неверный пароль",
            )

        return ResponseUserLogin(token=await create_access_token(
            data={"email": user.email, "user_id": user.id}
        ))


    async def find_user_by_email(
            self, user_email: EmailStr
    ) -> Optional[AllUserData]:
        """
        Поиск пользователя по email
        """
        async with self.uow:
            user_data = await self.uow.user.get_one(email=user_email)
            if user_data is None:
                return None
            return self._convert_to_user_data(user_data)

    @staticmethod
    def _convert_to_user_data(user_data: User) -> AllUserData:
        """
        Преобразование данных из SQLAlchemy в Pydantic модель
        """
        return AllUserData(
            id=user_data.id,
            email=user_data.email,
            username=user_data.username,
            data_register=user_data.data_register,
            password=user_data.password,
        )
