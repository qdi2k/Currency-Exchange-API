from os import path

from fastapi import HTTPException, BackgroundTasks, Request
from fastapi_mail import MessageSchema, MessageType, FastMail
from pydantic import EmailStr
from starlette import status
from starlette.datastructures import URL

from app.api.schemas.user import (RequestUserCreate, ResponseUserCreate,
                                  RequestUserLogin, ResponseUserLogin,
                                  ResponseAcceptUser)
from app.core.config import settings, BASE_DIR
from app.core.security import (get_password_hash, verify_password,
                               create_access_token,
                               generate_verification_token,
                               verify_verification_token)
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
        """Регистрация пользователя"""
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
            else:
                user_from_db = await self.uow.user.add_one(user_dict)
                verification_token = generate_verification_token(
                    user_id=user_from_db.id
                )
                await self.uow.user.update_one(
                    user_id=user_from_db.id,
                    data={"verification_token": verification_token}
                )
            await self.uow.commit()

        background_tasks.add_task(
            send_mail_confirm,
            request.base_url, user_data.email, verification_token
        )
        return ResponseUserCreate(
            message=(f"Мы отправили письмо по адресу {user_data.email}"
                     + " Нажмите на ссылку внутри, чтобы начать.")
        )

    async def register_confirm(self, key: str) -> ResponseAcceptUser:
        """Подтверждение регистрации пользователя."""
        user_id = verify_verification_token(token=key)
        if not user_id:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Неверный ключ подтверждения"
            )

        async with self.uow:
            user = await self.uow.user.get_one(id=user_id)
            if user.verified:
                raise HTTPException(
                    status_code=status.HTTP_405_METHOD_NOT_ALLOWED,
                    detail="Этот пользователь уже подтвердил свой аккаунт"
                )
            token = await create_access_token(
                data={"email": user.email, "user_id": user.id}
            )
            await self.uow.user.update_one(
                user_id = user_id, data = {"verified": True}
            )
            await self.uow.commit()
            return ResponseAcceptUser(token=token)

    async def login(self, user_data: RequestUserLogin) -> ResponseUserLogin:
        """Вход пользователя в систему."""
        async with self.uow:
            user = await self.uow.user.get_one(email=user_data.email)
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
            token = await create_access_token(
                data={"email": user.email, "user_id": user.id}
            )
            await self.uow.commit()
            return ResponseUserLogin(token=token)


async def send_mail_confirm(
    base_url: URL, email: EmailStr, verification_token: str
) -> None:
    """Отправка пользователю сообщения подтверждения регистрации."""
    url_confirm = (
        f'{base_url}api/auth/register-confirm/?'
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
