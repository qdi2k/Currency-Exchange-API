from typing import Annotated

from fastapi import APIRouter, Depends
from starlette import status

from app.api.schemas.currency import ResponseCurrencyList
from app.core.security import get_current_user
from app.utils.external_api import CurrencyAPI

currency_router = APIRouter(prefix="/currency", tags=["Currency"])


async def get_currency_service() -> CurrencyAPI:
    """
    Создает и возвращает экземпляр сервиса конвертации валют.
    """
    return CurrencyAPI()


@currency_router.get(
    path="/list/", response_model=ResponseCurrencyList,
    status_code=status.HTTP_200_OK,
)
async def currency_list(
        _: Annotated[str, Depends(get_current_user)],
        currency_service: CurrencyAPI = Depends(get_currency_service)
) -> ResponseCurrencyList:
    """
    ## Полный список поддерживаемых валют

    Отображение списка поддерживаемых валют и их кодов

    ---
    #### Возвращает следующие параметры:
    * `success` - булево сообщение, успешен ли выполняемый запрос

    * `symbols` - перечисление объектов содержащих кодировку
        валюты и его расшифровку
    ---
    """
    return await currency_service.get_currency_list()
