import logging
from typing import Dict, Any

import requests
from fastapi import HTTPException
from starlette import status
from requests.models import Response

from app.api.schemas.currency import (ResponseCurrencyList,
                                      RequestCurrencyExchange,
                                      ResponseCurrencyExchange)
from app.core.config import settings

logger = logging.getLogger()


class CurrencyAPI:
    """
    Логика работы со сторонним сервисом по конвертации валюты

    https://apilayer.com/marketplace/currency_data-api
    """

    logger = logging.getLogger()

    HEADERS = {"apikey": settings.CURRENCY_DATA_API}
    URL_GET_LIST = "https://api.apilayer.com/currency_data/list"
    PRE_URL_CONVERT = "https://api.apilayer.com/currency_data/convert"

    async def get_currency_list(self) -> ResponseCurrencyList:
        """Получить список конвертируемых валют."""
        response = requests.get(url=self.URL_GET_LIST, headers=self.HEADERS)
        return ResponseCurrencyList(
            **await self._get_json_data_or_503(response=response)
        )

    async def convert_currency(
            self, data: RequestCurrencyExchange
    ) -> ResponseCurrencyExchange:
        """Конвертация одной валюты в другую."""
        await self._check_currency(
            to_currency=data.to_currency, from_currency=data.from_currency
        )
        url = (
            f"{self.PRE_URL_CONVERT}?to={data.to_currency}"
            + f"&from={data.from_currency}&amount={data.amount}"
        )
        json_data = await self._get_json_data_or_503(
            response=requests.get(url=url, headers=self.HEADERS)
        )
        return ResponseCurrencyExchange(
            **{**data.model_dump(), "result": json_data.get("result")}
        )

    async def _get_json_data_or_503(
            self, response: Response
    ) -> Dict[str, Any]:
        """Возврат тела ответа или логирование и райз ошибки сервера."""
        json_data = response.json()
        if (response.status_code != status.HTTP_200_OK
                or json_data.get("success") is False
                or json_data.get("error")):
            self.logger.error(response.status_code)
            self.logger.error(response.text)
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Сервис в данный момент недоступен"
            )
        return json_data

    async def _check_currency(
            self, from_currency: str, to_currency: str
    ) -> None:
        """Проверка доступности валют."""
        currency_list = await self.get_currency_list()
        if not currency_list.currencies.get(from_currency):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=(
                    f"Валюта from_currency = {from_currency}"
                    + f" не поддерживается [Попробуйте from_currency = EUR]."
                )
            )
        if not currency_list.currencies.get(to_currency):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=(
                    f"Валюта to_currency = {to_currency}"
                    + f" не поддерживается [Попробуйте to_currency = RUB]."
                )
            )
