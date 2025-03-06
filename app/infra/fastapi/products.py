from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel

from app.infra.core.errors import DoesNotExistError, ExistsError
from app.infra.core.repository.products import ProductRepository, Product
from app.infra.fastapi.dependables import get_product_repository

router = APIRouter(prefix="/products", tags=["Products"])


class ProductCreateRequest(BaseModel):
    name: str
    barcode: str
    price: float


class ProductUpdateRequest(BaseModel):
    price: float


class ProductResponse(BaseModel):
    id: UUID
    name: str
    barcode: str
    price: float


class ProductsResponse(BaseModel):
    products: list[ProductResponse]


def _to_response(product: Product) -> ProductResponse:
    return ProductResponse(
        id=product.id,
        name=product.name,
        barcode=product.barcode,
        price=product.price,
    )


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
    return _to_response(product)


@router.get("/{product_id}", response_model=ProductResponse)
def get_product(
        product_id: UUID,
        repo: ProductRepository = Depends(get_product_repository),
) -> ProductResponse:
    try:
        product = repo.read(product_id)
    except DoesNotExistError as e:
        raise HTTPException(status_code=404, detail=str(e))
    return _to_response(product)


@router.get("", response_model=ProductsResponse)
def list_products(
        repo: ProductRepository = Depends(get_product_repository),
) -> ProductsResponse:
    products = repo.read_list()
    return ProductsResponse(products=[_to_response(p) for p in products])


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
