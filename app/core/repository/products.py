from __future__ import annotations

from dataclasses import dataclass, field
from typing import Protocol
from uuid import UUID, uuid4


class ProductRepository(Protocol):
    def exists(self, product_id) -> bool: ...

    def add(self, product: Product) -> None: ...

    def read(self, product_id: UUID) -> Product: ...

    def read_list(self) -> list[Product]: ...

    def update_price(self, product_id: UUID, price: float) -> None: ...

    def update_receipt_id(self, product_id: UUID, receipt_id: UUID) -> None: ...

    def clear(self) -> None: ...


@dataclass
class Product:
    name: str
    barcode: str
    price: float
    id: UUID = field(default_factory=uuid4)
