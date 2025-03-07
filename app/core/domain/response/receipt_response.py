from typing import List, Optional
from uuid import UUID

from pydantic import BaseModel

from app.core.domain.response.product_response import ProductResponse


class ReceiptResponse(BaseModel):
    receipt_id: Optional[UUID] = None
    shift_id: UUID
    products: List[ProductResponse]

    class Builder:
        def __init__(self):
            self.receipt_id = None
            self.shift_id = None
            self.products = []

        def with_receipt_id(self, receipt_id: UUID) -> "ReceiptResponse.Builder":
            self.receipt_id = receipt_id
            return self

        def with_shift_id(self,
                          shift_id: UUID) -> "ReceiptResponse.Builder":
            self.shift_id = shift_id
            return self

        def with_products(
                self, products: List[ProductResponse]
        ) -> "ReceiptResponse.Builder":
            self.products = products
            return self

        def add_product(self, product: ProductResponse) -> "ReceiptResponse.Builder":
            self.products.append(product)
            return self

        def build(self) -> "ReceiptResponse":
            return ReceiptResponse(receipt_id=self.receipt_id, shift_id=self.shift_id,
                                   products=self.products)

    @classmethod
    def builder(cls) -> Builder:
        return cls.Builder()
