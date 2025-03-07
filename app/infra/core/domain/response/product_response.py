from typing import Optional
from uuid import UUID

from pydantic import BaseModel


class ProductResponse(BaseModel):
    id: Optional[UUID] = None
    name: Optional[str] = None
    barcode: Optional[str] = None
    price: Optional[float] = None

    class Builder:
        def __init__(self):
            self.id = None
            self.name = None
            self.barcode = None
            self.price = None

        def with_id(self, id: UUID) -> "ProductResponse.Builder":
            self.id = id
            return self

        def with_name(self, name: str) -> "ProductResponse.Builder":
            self.name = name
            return self

        def with_barcode(self, barcode: str) -> "ProductResponse.Builder":
            self.barcode = barcode
            return self

        def with_price(self, price: float) -> "ProductResponse.Builder":
            self.price = price
            return self

        def build(self) -> "ProductResponse":
            return ProductResponse(
                id=self.id, name=self.name, barcode=self.barcode, price=self.price
            )

    @classmethod
    def builder(cls) -> Builder:
        return cls.Builder()
