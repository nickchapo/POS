from app.core.domain.response.payment_response import PaymentResponse
from app.core.repository.payments import Payment


class PaymentMapper:
    @staticmethod
    def to_response(payment: Payment) -> PaymentResponse:
        return (
            PaymentResponse.builder()
            .with_receipt_id(payment.receipt_id)
            .with_amount(payment.amount)
            .with_currency(payment.currency)
            .build()
        )
