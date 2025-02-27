from typing import Annotated

from fastapi import Depends, Request

from app.infra.core.products import ProductRepository
from app.infra.core.shifts import ShiftRepository


def get_product_repository(request: Request) -> ProductRepository:
    return request.app.state.products


def get_shift_repository(request: Request) -> ShiftRepository:
    return request.app.state.shifts


ProductRepositoryDependable = Annotated[
    ProductRepository, Depends(get_product_repository)]

ShiftRepositoryDependable = Annotated[
    ShiftRepository, Depends(get_shift_repository)
]
