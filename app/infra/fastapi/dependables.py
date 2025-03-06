from typing import Annotated, cast

from fastapi import Depends, Request

from app.infra.core.products import ProductRepository
from app.infra.core.shifts import ShiftRepository
from app.infra.core.repository.receipt_repository import ReceiptRepository


def get_product_repository(request: Request) -> ProductRepository:
    return cast(ProductRepository, request.app.state.products)


def get_shift_repository(request: Request) -> ShiftRepository:
    return cast(ShiftRepository, request.app.state.shifts)


def get_receipt_repository(request: Request) -> ReceiptRepository:
    return cast(ReceiptRepository, request.app.state.receipts)


ProductRepositoryDependable = Annotated[
    ProductRepository, Depends(get_product_repository)
]

ShiftRepositoryDependable = Annotated[ShiftRepository, Depends(get_shift_repository)]

ReceiptRepositoryDependable = Annotated[
    ReceiptRepository, Depends(get_receipt_repository)
]
