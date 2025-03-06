from dataclasses import dataclass, field
from typing import List
from uuid import UUID, uuid4

from app.infra.core.products import Product


@dataclass
class Receipt:
    id: UUID = field(default_factory=uuid4)
    products: List[Product] = field(default_factory=list)
