from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException

from app.core.domain.request.product_requests import (
    ProductCreateRequest,
    ProductUpdateRequest,
)
from app.core.domain.response.product_response import ProductResponse
from app.core.domain.response.products_response import ProductsResponse
from app.core.errors import DoesNotExistError, ExistsError
from app.core.mapper.product_mapper import ProductMapper
from app.core.repository.products import Product, ProductRepository
from app.infra.fastapi.dependables import get_product_repository

router = APIRouter(prefix="/products", tags=["Products"])


@router.post("", response_model=ProductResponse, status_code=201)
def create_product(
        request: ProductCreateRequest,
        repo: ProductRepository = Depends(get_product_repository),
) -> ProductResponse:
    product = Product(**request.model_dump())
    try:
        repo.add(product)
    except ExistsError as e:
        raise HTTPException(status_code=409, detail=str(e))
    except DoesNotExistError as e:
        raise HTTPException(status_code=404, detail=str(e))
    return ProductMapper.to_response(product)


@router.get("/{product_id}", response_model=ProductResponse)
def get_product(
        product_id: UUID,
        repo: ProductRepository = Depends(get_product_repository),
) -> ProductResponse:
    try:
        product = repo.read(product_id)
    except DoesNotExistError as e:
        raise HTTPException(status_code=404, detail=str(e))
    return ProductMapper.to_response(product)


@router.get("", response_model=ProductsResponse)
def list_products(
        repo: ProductRepository = Depends(get_product_repository),
) -> ProductsResponse:
    products = repo.read_list()
    return ProductsResponse(products=[ProductMapper.to_response(p) for p in products])


@router.patch("/{product_id}", status_code=200)
def update_product(
        product_id: UUID,
        request: ProductUpdateRequest,
        repo: ProductRepository = Depends(get_product_repository),
) -> dict[str, str]:
    try:
        repo.update_price(product_id, request.price)
    except DoesNotExistError as e:
        raise HTTPException(status_code=404, detail=str(e))
    return {"detail": "Product updated successfully"}
