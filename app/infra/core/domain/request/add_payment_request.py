from pydantic import BaseModel

from app.infra.core.currency import Currency


class AddPaymentRequest(BaseModel):
    currency: Currency
    amount: float
