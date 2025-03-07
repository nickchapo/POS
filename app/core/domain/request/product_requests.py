from pydantic import BaseModel


class ProductCreateRequest(BaseModel):
    name: str
    barcode: str
    price: float


class ProductUpdateRequest(BaseModel):
    price: float
