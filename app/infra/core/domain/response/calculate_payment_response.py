from typing import Optional
from uuid import UUID

from pydantic import BaseModel

from app.infra.core.currency import Currency


class CalculatePaymentResponse(BaseModel):
    receipt_id: Optional[UUID] = None
    amount: Optional[float] = None
    currency: Optional[Currency] = None

    class Builder:
        def __init__(self):
            self.receipt_id = None
            self.amount = None
            self.currency = None

        def with_receipt_id(self,
                            receipt_id: UUID) -> 'CalculatePaymentResponse.Builder':
            self.receipt_id = receipt_id
            return self

        def with_amount(self, amount: float) -> 'CalculatePaymentResponse.Builder':
            self.amount = amount
            return self

        def with_currency(self, currency: Currency) -> 'CalculatePaymentResponse.Builder':
            self.currency = currency
            return self

        def build(self) -> 'CalculatePaymentResponse':
            return CalculatePaymentResponse(
                receipt_id=self.receipt_id,
                amount=self.amount,
                currency=self.currency
            )

    @classmethod
    def builder(cls) -> Builder:
        return cls.Builder()
