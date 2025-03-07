from pydantic import BaseModel

from app.core.currency import Currency


class AddPaymentRequest(BaseModel):
    currency: Currency
    amount: float
