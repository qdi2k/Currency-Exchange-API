from typing import Annotated

from fastapi import APIRouter, Depends
from starlette import status

from app.api.schemas.currency import (ResponseCurrencyList,
                                      RequestCurrencyExchange,
                                      ResponseCurrencyExchange)
from app.core.exception import responses_err
from app.core.security import get_current_user
from app.utils.external_api import CurrencyAPI

currency_router = APIRouter(
    prefix="/currency", tags=["Currency"],
    responses={
        **responses_err.service_unavailable_entity(),
        **responses_err.unauthorized_entity()
    }
)


async def get_currency_service() -> CurrencyAPI:
    """
    Создает и возвращает экземпляр сервиса конвертации валют.
    """
    return CurrencyAPI()


@currency_router.get(
    path="/list/", response_model=ResponseCurrencyList,
    status_code=status.HTTP_200_OK,
    responses={**responses_err.bad_request_entity()}
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


@currency_router.post(
    path="/exchange/", response_model=ResponseCurrencyExchange,
    status_code=status.HTTP_200_OK,
)
async def currency_exchange(
        currency_data: RequestCurrencyExchange,
        _: Annotated[str, Depends(get_current_user)],
        currency_service: CurrencyAPI = Depends(get_currency_service)
) -> ResponseCurrencyExchange:
    """
    ## Конвертация валюты

    Получение свежих обменных курсов для различных валют из открытого
    API обменных курсов
    ---
    #### Принимает на вход следующие параметры:
    * `from_currency` - какую валюту нужно преобразовать

    * `to_currency` - в какую валюту нужно преобразовать

    * `amount` - количество валюты

    #### Возвращает следующие параметры:
    * `from_currency` - какая валюта преобразована

    * `to_currency` - в какую валюту преобразована

    * `amount` - количество валюты

    * `result` - результат преобразования
    ---
    """
    return await currency_service.convert_currency(data=currency_data)
