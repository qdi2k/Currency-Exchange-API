import logging
from typing import Dict, Any

import requests
from fastapi import HTTPException
from starlette import status
from requests.models import Response

from app.api.schemas.currency import ResponseCurrencyList
from app.core.config import settings

logger = logging.getLogger()


class CurrencyAPI:
    """
    Логика работы со сторонним сервисом по конвертации валюты
    https://apilayer.com/marketplace/currency_data-api
    """
    logger = logging.getLogger()

    headers = {"apikey": settings.CURRENCY_DATA_API}
    url_get_list = "https://api.apilayer.com/currency_data/list"

    async def get_currency_list(self) -> ResponseCurrencyList:
        """Получить список конвертируемых валют."""
        response = requests.get(url=self.url_get_list, headers=self.headers)
        return ResponseCurrencyList(
            **await self.get_json_data_or_503(response=response)
        )

    async def get_json_data_or_503(
            self, response: Response
    ) -> Dict[str, Any]:
        """Возврат тела ответа или райз ошибки сервера."""
        json_data = response.json()
        if (response.status_code != status.HTTP_200_OK
                or json_data.get("error")):
            self.logger.error(response.status_code)
            self.logger.error(response.text)
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Сервис в данный момент недоступен"
            )
        return json_data
