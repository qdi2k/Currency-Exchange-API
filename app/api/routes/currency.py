import logging
from typing import Annotated

import requests
from fastapi import APIRouter, HTTPException, Depends
from starlette import status

from app.api.schemas.currency import ResponseCurrencyList
from app.core.config import settings
from app.core.security import get_current_user

logger = logging.getLogger()
currency_router = APIRouter(prefix="/currency", tags=["Currency"])


@currency_router.get(path="/list/", response_model=ResponseCurrencyList)
async def get_currency_list(
        _: Annotated[str, Depends(get_current_user)]
) -> ResponseCurrencyList:
    url = "https://api.apilayer.com/currency_data/list"
    headers = {
        "apikey": settings.CURRENCY_DATA_API
    }
    response = requests.get(url=url, headers=headers)
    json_data = response.json()

    if response.status_code != status.HTTP_200_OK or json_data.get("error"):
        logger.error(response.status_code)
        logger.error(response.text)
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Сервис в данный момент недоступен"
        )

    return ResponseCurrencyList(**json_data)
