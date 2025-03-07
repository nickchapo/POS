from pydantic import BaseModel

from app.core.domain.response.product_response import ProductResponse


class ProductsResponse(BaseModel):
    products: list[ProductResponse]
