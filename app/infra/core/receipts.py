from dataclasses import dataclass, field
from typing import List, Protocol
from uuid import UUID, uuid4


@dataclass
class Receipt:
    id: UUID = field(default_factory=uuid4)
    product_ids: List[UUID] = field(default_factory=list)


class ReceiptRepository(Protocol):
    def exists(self, receipt_id) -> bool: ...

    def get(self, receipt_id: UUID) -> Receipt | None: ...

    def add(self, receipt: Receipt) -> None: ...

    def clear(self) -> None: ...
