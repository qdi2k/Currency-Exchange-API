from fastapi import APIRouter, Depends

from app.api.schemas.auth import ResponseUserLogin, RequestUserCreate, \
    ResponseUserCreate
from app.services.user_service import UserService
from app.utils.unitofwork import IUnitOfWork, UnitOfWork

user_router = APIRouter(prefix="/auth", tags=["Auth"])


async def get_user_service(
        uow: IUnitOfWork = Depends(UnitOfWork)
) -> UserService:
    return UserService(uow)


@user_router.post("/register/")
async def create_user(
        user_data: RequestUserCreate,
        user_service: UserService = Depends(get_user_service)
):
    return await user_service.registration(user_data=user_data)
