from app.infra.core.domain.response.product_response import ProductResponse
from app.infra.core.repository.products import Product


class ProductMapper:
    @staticmethod
    def to_response(product: Product) -> ProductResponse:
        return ProductResponse.builder() \
            .with_id(product.id) \
            .with_name(product.name) \
            .with_barcode(product.barcode) \
            .with_price(product.price) \
            .build()
