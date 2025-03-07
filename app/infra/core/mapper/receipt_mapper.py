from app.infra.core.domain.response.receipt_response import ReceiptResponse
from app.infra.core.mapper.product_mapper import ProductMapper
from app.infra.core.repository.receipts import Receipt


class ReceiptMapper:
    @staticmethod
    def to_response(receipt: Receipt) -> ReceiptResponse:
        return ReceiptResponse.builder() \
            .with_receipt_id(receipt.id) \
            .with_products([ProductMapper.to_response(product) for product in receipt.products]) \
            .build()
