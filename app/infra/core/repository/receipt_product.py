from typing import Protocol
from uuid import UUID


class ReceiptProductRepository(Protocol):

    def add_receipt_product(self, receipt_id: UUID, product_id: UUID) -> None: ...
