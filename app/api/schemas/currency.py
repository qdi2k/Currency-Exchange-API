from pydantic import BaseModel, Field
from typing import Dict


class ResponseCurrencyList(BaseModel):
    currencies: Dict[str, str]


class RequestCurrencyExchange(BaseModel):
    from_currency: str = Field(
        pattern=r'^[A-Za-z]{3}', min_length=3, max_length=3
    )
    to_currency: str = Field(
        pattern=r'^[A-Za-z]{3}', min_length=3, max_length=3
    )
    amount: float = 1


class ResponseCurrencyExchange(RequestCurrencyExchange):
    result: float = 1
