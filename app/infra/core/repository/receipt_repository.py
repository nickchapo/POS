from typing import Protocol
from uuid import UUID

from app.infra.core.entity.receipt import Receipt


class ReceiptRepository(Protocol):
    def get(self, receipt_id: UUID) -> Receipt: ...

    def add(self, receipt: Receipt) -> None: ...

    def clear(self) -> None: ...
