from fastapi import APIRouter, Depends

from app.api.schemas.auth import (ResponseUserLogin, RequestUserCreate,
                                  ResponseUserCreate, RequestUserLogin)
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


@user_router.post("/register/", response_model=ResponseUserCreate)
async def create_user(
        user_data: RequestUserCreate,
        user_service: AuthUserService = Depends(get_user_service)
):
    return await user_service.registration(user_data=user_data)


@user_router.post("/login/", response_model=ResponseUserLogin)
async def user_login(
        user_data: RequestUserLogin,
        user_service: AuthUserService = Depends(get_user_service)
):
    return await user_service.login(user_data=user_data)
