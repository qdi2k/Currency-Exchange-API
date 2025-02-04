from pydantic import BaseModel
from typing import Dict


class ResponseCurrencyList(BaseModel):
    success: bool
    currencies: Dict[str, str]
