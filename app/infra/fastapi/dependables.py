from typing import Annotated, cast

from fastapi import Depends, Request

from app.infra.core.adapter.exchange_rate_adapter import ExchangeRateAdapter
from app.infra.core.repository.payments import PaymentRepository
from app.infra.core.repository.products import ProductRepository
from app.infra.core.repository.receipts import ReceiptRepository
from app.infra.core.repository.shifts import ShiftRepository
from app.infra.core.service.payments import PaymentService
from app.infra.core.service.receipts import ReceiptService


def get_product_repository(request: Request) -> ProductRepository:
    return cast(ProductRepository, request.app.state.products)


def get_shift_repository(request: Request) -> ShiftRepository:
    return cast(ShiftRepository, request.app.state.shifts)


def get_receipt_repository(request: Request) -> ReceiptRepository:
    return cast(ReceiptRepository, request.app.state.receipts)


def get_payments_repository(request: Request) -> PaymentRepository:
    return cast(PaymentRepository, request.app.state.payments)


def get_receipt_service(
    receipt_repo: ReceiptRepository = Depends(get_receipt_repository),
    product_repo: ProductRepository = Depends(get_product_repository),
) -> ReceiptService:
    return ReceiptService(
        receipt_repository=receipt_repo, product_repository=product_repo
    )


def get_payment_service(
    payment_repo: PaymentRepository = Depends(get_payments_repository),
    receipt_service: ReceiptService = Depends(get_receipt_service),
) -> PaymentService:
    return PaymentService(
        receipt_service=receipt_service,
        payment_repository=payment_repo,
        exchange_rate_target=ExchangeRateAdapter(),
    )


ProductRepositoryDependable = Annotated[
    ProductRepository, Depends(get_product_repository)
]

ShiftRepositoryDependable = Annotated[ShiftRepository, Depends(get_shift_repository)]

ReceiptRepositoryDependable = Annotated[
    ReceiptRepository, Depends(get_receipt_repository)
]

ReceiptServiceDependable = Annotated[ReceiptRepository, Depends(get_receipt_service)]
