from __future__ import annotations

from dataclasses import dataclass, field
from typing import Protocol
from uuid import UUID, uuid4


class ProductRepository(Protocol):
    def add(self, product: Product) -> None:
        ...

    def read(self, product_id: UUID) -> Product:
        ...

    def read_list(self) -> list[Product]:
        ...

    def update_price(self, product_id: UUID, price: float) -> None:
        ...

    def clear(self) -> None:
        ...


@dataclass
class Product:
    name: str
    barcode: str
    price: float
    id: UUID = field(default_factory=uuid4)
