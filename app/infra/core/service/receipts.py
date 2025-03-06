from dataclasses import dataclass
from typing import List
from uuid import UUID

from app.infra.core.errors import DoesNotExistError
from app.infra.core.products import ProductRepository, Product
from app.infra.core.receipt_product import ReceiptProductRepository
from app.infra.core.receipts import ReceiptRepository, Receipt


@dataclass(frozen=True)
class ReceiptResponse:
    receipt_id: UUID
    products: List[Product]


@dataclass
class ReceiptService:
    receipt_repository: ReceiptRepository
    product_repository: ProductRepository
    receipt_product_repository: ReceiptProductRepository

    def get_receipt(self, receipt_id) -> ReceiptResponse:
        receipt = self.receipt_repository.get(receipt_id)
        if not receipt:
            raise DoesNotExistError("Receipt", "id", str(receipt_id))

        product_ids = receipt.product_ids
        products = [self.product_repository.read(product_id) for product_id in product_ids]
        return ReceiptResponse(receipt_id=receipt_id, products=products)

    def add_receipt(self) -> ReceiptResponse:
        receipt = Receipt()
        self.receipt_repository.add(receipt)
        return self.get_receipt(receipt.id)

    def add_product(self, receipt_id: UUID, product_id: UUID) -> ReceiptResponse:
        if not self.receipt_repository.exists(receipt_id):
            raise DoesNotExistError("Receipt", "id", str(receipt_id))

        if not self.product_repository.exists(product_id):
            raise DoesNotExistError("Product", "id", str(product_id))

        self.receipt_product_repository.add_receipt_product(receipt_id, product_id)

        return self.get_receipt(receipt_id)
