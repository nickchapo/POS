from app.core.domain.response.receipt_response import ReceiptResponse
from app.core.mapper.product_mapper import ProductMapper
from app.core.repository.receipts import Receipt


class ReceiptMapper:
    @staticmethod
    def to_response(receipt: Receipt) -> ReceiptResponse:
        return (
            ReceiptResponse.builder()
            .with_receipt_id(receipt.id)
            .with_shift_id(receipt.shift_id)
            .with_products(
                [ProductMapper.to_response(product) for product in receipt.products]
            )
            .build()
        )
