from asyncio import Protocol
from dataclasses import dataclass
from datetime import datetime
from typing import List
from uuid import UUID, uuid4

from app.infra.core.currency import Currency


@dataclass
class Payment:
    id: UUID = uuid4()
    receipt_id: UUID = None
    amount: float = 0.0
    currency: Currency = Currency.GEL
    created_at: datetime = datetime.now()


class PaymentRepository(Protocol):
    def add(self, payment: Payment) -> Payment: ...

    def get(self, payment_id: UUID) -> Payment | None: ...

    def get_all(self) -> List[Payment]: ...

    def receipt_has_payment(self, receipt_id: UUID) -> bool: ...
