from os import path
from typing import Optional

from fastapi import HTTPException, BackgroundTasks, Request
from fastapi_mail import MessageSchema, MessageType, FastMail
from pydantic import EmailStr
from starlette import status
from starlette.datastructures import URL

from app.api.schemas.auth import (RequestUserCreate, ResponseUserCreate,
                                  RequestUserLogin, ResponseUserLogin,
                                  UserSchema)
from app.core.config import settings, BASE_DIR
from app.core.security import (get_password_hash, verify_password,
                               create_access_token,
                               generate_verification_token)
from app.utils.unitofwork import IUnitOfWork


class AuthUserService:
    """
    Бизнес логика работы с пользователями
    """

    def __init__(self, uow: IUnitOfWork):
        self.uow = uow

    async def registration(
            self, request: Request, user_data: RequestUserCreate,
            background_tasks: BackgroundTasks
    ) -> ResponseUserCreate:
        """
        Регистрация пользователя
        """
        async with self.uow:
            user = await self.uow.user.get_one(email=user_data.email)

            if user and user.verified:
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail="Пользователь с таким Email уже существует"
                )

            user_data.password = get_password_hash(password=user_data.password)
            user_dict = user_data.model_dump()

            if user and not user.verified:
                verification_token = generate_verification_token(
                    user_id=user.id
                )
                user_dict["verification_token"] = verification_token
                await self.uow.user.update_one(user.id, user_dict)
                user_from_db = await self.uow.user.get_one(id=user.id)
            else:
                user_from_db = await self.uow.user.add_one(user_dict)
                verification_token = generate_verification_token(
                    user_id=user_from_db.id
                )
                await self.uow.user.update_one(
                    user_id=user_from_db.id,
                    data={"verification_token": verification_token}
                )

            background_tasks.add_task(
                send_mail_confirm,
                request.base_url, user_from_db.email, verification_token
            )
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
    ) -> Optional[UserSchema]:
        """Поиск пользователя по email."""
        async with self.uow:
            user_data = await self.uow.user.get_one(email=user_email)
            if user_data is None:
                return None
            return user_data


async def send_mail_confirm(
    base_url: URL, email: EmailStr, verification_token: str
) -> None:
    """Отправка пользователю сообщения подтверждения регистрации."""
    url_confirm = (
        f'{base_url}api/auth/register-confirm?'
        + f'key={verification_token}'
    )

    template_path = path.join(BASE_DIR, 'template/register_confirm.html')
    with open(template_path, "r", encoding="utf-8") as file:
        html_template = file.read()
    html = html_template.format(url_confirm=url_confirm)

    message = MessageSchema(
        subject="Подтвердите регистрацию на Currency Exchange",
        recipients=[email],
        body=html,
        subtype=MessageType.html,
        bcc=[]
    )
    fm = FastMail(settings.MAIL_CONF)
    await fm.send_message(message)
