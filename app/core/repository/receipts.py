from dataclasses import dataclass, field
from typing import List, Protocol
from uuid import UUID, uuid4

from app.core.repository.products import Product


@dataclass
class Receipt:
    id: UUID = field(default_factory=uuid4)
    shift_id: UUID = field(default_factory=uuid4)
    products: List[Product] = field(default_factory=list)


class ReceiptRepository(Protocol):
    def exists(self, receipt_id) -> bool: ...

    def get(self, receipt_id: UUID) -> Receipt | None: ...

    def add(self, receipt: Receipt) -> Receipt: ...

    def clear(self) -> None: ...

    def get_by_shift(self, shift_id: UUID) -> List[Receipt]: ...
