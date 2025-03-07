from pydantic import BaseModel

from app.core.currency import Currency


class QuoteRequest(BaseModel):
    currency: Currency
