from dataclasses import dataclass
from uuid import UUID

from app.infra.core.domain.response.receipt_response import ReceiptResponse
from app.infra.core.errors import DoesNotExistError, ExistsError
from app.infra.core.mapper.receipt_mapper import ReceiptMapper
from app.infra.core.repository.products import ProductRepository
from app.infra.core.repository.receipts import ReceiptRepository, Receipt


@dataclass
class ReceiptService:
    receipt_repository: ReceiptRepository
    product_repository: ProductRepository

    def get_receipt(self, receipt_id) -> ReceiptResponse:
        receipt = self.receipt_repository.get(receipt_id)
        if not receipt:
            raise DoesNotExistError("Receipt", "id", str(receipt_id))
        return ReceiptMapper.to_response(receipt)

    def add_receipt(self) -> ReceiptResponse:
        receipt = Receipt()
        return ReceiptMapper.to_response(self.receipt_repository.add(receipt))

    def add_product(self, receipt_id: UUID, product_id: UUID) -> ReceiptResponse:
        if not self.product_repository.exists(product_id):
            raise DoesNotExistError("Product", "id", str(product_id))

        receipt = self.receipt_repository.get(receipt_id)
        if not receipt:
            raise DoesNotExistError("Receipt", "id", str(receipt_id))
        product_ids = [p.id for p in receipt.products]
        if product_id in product_ids:
            raise ExistsError("Product", "id", str(product_id))

        self.product_repository.update_receipt_id(product_id, receipt_id)

        return self.get_receipt(receipt_id)
