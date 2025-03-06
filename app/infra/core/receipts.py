from dataclasses import dataclass, field
from typing import List, Protocol
from uuid import UUID, uuid4

from app.infra.core.products import Product


@dataclass
class Receipt:
    id: UUID = field(default_factory=uuid4)
    products: List[Product] = field(default_factory=list)

class ReceiptRepository(Protocol):
    def get(self, receipt_id: UUID) -> Receipt: ...

    def add(self, receipt: Receipt) -> None: ...

    def add_product(self, receipt_id: UUID, product_id: UUID) -> None: ...

    def clear(self) -> None: ...
