from pydantic import BaseModel

from app.infra.core.currency import Currency


class QuoteRequest(BaseModel):
    currency: Currency
