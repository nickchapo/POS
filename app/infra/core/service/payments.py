from dataclasses import dataclass
from uuid import UUID

from app.infra.core.adapter.exchange_rate_target import ExchangeRateTarget
from app.infra.core.currency import Currency
from app.infra.core.domain.response.calculate_payment_response import CalculatePaymentResponse
from app.infra.core.errors import ExistsError
from app.infra.core.repository.payments import PaymentRepository
from app.infra.core.service.receipts import ReceiptService


@dataclass
class PaymentService:
    receipt_service: ReceiptService
    exchange_rate_target: ExchangeRateTarget
    payment_repository: PaymentRepository

    def calculate_total(self, receipt_id: UUID, currency: Currency = Currency.GEL) -> CalculatePaymentResponse:
        if self.payment_repository.receipt_has_payment(receipt_id):
            raise ExistsError("Payment", "receipt_id", str(receipt_id))

        receipt = self.receipt_service.get_receipt(receipt_id)
        total_gel = sum(product.price for product in receipt.products)

        if currency == Currency.GEL:
            return CalculatePaymentResponse.builder() \
                .with_receipt_id(receipt_id) \
                .with_amount(total_gel) \
                .with_currency(currency) \
                .build()

        exchange_rate = self.exchange_rate_target.get_exchange_rate(Currency.GEL, currency)
        converted_amount = total_gel * exchange_rate

        return CalculatePaymentResponse.builder() \
            .with_receipt_id(receipt_id) \
            .with_amount(round(converted_amount, 2)) \
            .with_currency(currency) \
            .build()
