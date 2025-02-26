from typing import Annotated

from fastapi import Depends, Request

from app.infra.core.products import ProductRepository


def get_product_repository(request: Request) -> ProductRepository:
    return request.app.state.products


ProductRepositoryDependable = Annotated[
    ProductRepository, Depends(get_product_repository)]
