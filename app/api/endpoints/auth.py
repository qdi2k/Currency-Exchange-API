from fastapi import APIRouter, Depends, BackgroundTasks, Request, Query
from starlette import status

from app.api.schemas.user import (ResponseUserLogin, RequestUserCreate,
                                  ResponseUserCreate, RequestUserLogin,
                                  ResponseAcceptUser)
from app.services.user_service import AuthUserService
from app.utils.unitofwork import IUnitOfWork, UnitOfWork

user_router = APIRouter(prefix="/auth", tags=["Auth"])


async def get_user_service(
        uow: IUnitOfWork = Depends(UnitOfWork)
) -> AuthUserService:
    """
    Создает и возвращает экземпляр сервиса аутентификации пользователей.
    """
    return AuthUserService(uow)


@user_router.post(
    path="/register/", response_model=ResponseUserCreate,
    status_code=status.HTTP_201_CREATED,
)
async def create_user(
        request: Request,
        user_data: RequestUserCreate, background_tasks: BackgroundTasks,
        user_service: AuthUserService = Depends(get_user_service)
):
    """
    ## Регистрация пользователей

    Добавляет запись в БД о пользователе и отправляет на указанную почту
    письмо для подтверждения регистрации
    ---
    #### Принимает на вход следующие параметры:
    * `password` - пароль пользователя

    * `email` - электронная почта пользователя

    * `username` - имя пользователя

    #### Возвращает следующие параметры:
    * `message` - сообщение о том, что было отправлено письмо на почту для
    подтверждения регистрации
    ---
    """
    return await user_service.registration(
        request=request, user_data=user_data,
        background_tasks=background_tasks
    )


@user_router.get(
    path="/register-confirm/", response_model=ResponseAcceptUser,
    status_code=status.HTTP_200_OK,
)
async def accept_user(
        user_service: AuthUserService = Depends(get_user_service),
        key: str = Query(description="Ключ подтверждения регистрации")
):
    """
    ## Подтверждение регистрации пользователя

    Подтверждает статус пользователя как "зарегистрированный" и предоставляет
    доступ к аккаунту.
    ---
    #### Принимает на вход следующие параметры:
    * `key` - ключ для подтверждения регистрации

    #### Возвращает следующие параметры:
    * `message` - сообщение об успешной регистрации пользователя

    * `token` - токен для пользования ресурсом
    ---
    """
    return await user_service.register_confirm(key=key)


@user_router.post("/login/", response_model=ResponseUserLogin)
async def user_login(
        user_data: RequestUserLogin,
        user_service: AuthUserService = Depends(get_user_service)
):
    return await user_service.login(user_data=user_data)
