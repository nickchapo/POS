import sqlite3
import uuid

import pytest

from app.infra.core.errors import DoesNotExistError
from app.infra.core.products import Product
from app.infra.core.service.receipts import ReceiptService
from app.infra.sqlite.products import ProductSQLite
from app.infra.sqlite.receipt_product import ReceiptProductSqlLite
from app.infra.sqlite.receipts import ReceiptSqlLite


@pytest.fixture(scope="session")
def connection() -> sqlite3.Connection:
    conn = sqlite3.connect(":memory:")
    yield conn
    conn.close()


@pytest.fixture(scope="session", autouse=True)
def init_db(connection: sqlite3.Connection):
    ReceiptSqlLite(connection=connection)
    ProductSQLite(connection=connection)
    ReceiptProductSqlLite(connection=connection)


@pytest.fixture
def receipt_repo(connection: sqlite3.Connection) -> ReceiptSqlLite:
    repository = ReceiptSqlLite(connection=connection)
    return repository


@pytest.fixture
def product_repo(connection: sqlite3.Connection) -> ProductSQLite:
    repository = ProductSQLite(connection=connection)
    return repository


@pytest.fixture
def receipt_product_repo(connection: sqlite3.Connection) -> ReceiptProductSqlLite:
    repository = ReceiptProductSqlLite(connection=connection)
    return repository


@pytest.fixture
def receipt_service(receipt_repo: ReceiptSqlLite, product_repo: ProductSQLite,
                    receipt_product_repo: ReceiptProductSqlLite) -> ReceiptService:
    return ReceiptService(receipt_repository=receipt_repo, product_repository=product_repo,
                          receipt_product_repository=receipt_product_repo)


def test_add_nonexisting_product(receipt_service: ReceiptService) -> None:
    receipt = receipt_service.add_receipt()
    product_id = uuid.uuid4()

    with pytest.raises(DoesNotExistError):
        receipt_service.add_product(receipt_id=receipt.receipt_id, product_id=product_id)


def test_add_products_and_get_receipt(receipt_service: ReceiptService, product_repo: ProductSQLite):
    receipt = receipt_service.add_receipt()

    product1 = Product(id=uuid.uuid4(), name="Product1", barcode="barcode1", price=10.0)
    product2 = Product(id=uuid.uuid4(), name="Product2", barcode="barcode2", price=20.0)
    product_repo.add(product1)
    product_repo.add(product2)

    receipt_service.add_product(receipt.receipt_id, product1.id)
    receipt_service.add_product(receipt.receipt_id, product2.id)

    retrieved = receipt_service.get_receipt(receipt.receipt_id)

    product_map = {p.id: p for p in retrieved.products}
    assert len(product_map) == 2

    prod1 = product_map.get(product1.id)
    assert prod1 is not None, "Product1 not found in the receipt"
    assert prod1.name == product1.name, f"Expected name {product1.name}, got {prod1.name}"
    assert prod1.barcode == product1.barcode, f"Expected barcode {product1.barcode}, got {prod1.barcode}"
    assert prod1.price == product1.price, f"Expected price {product1.price}, got {prod1.price}"

    prod2 = product_map.get(product2.id)
    assert prod2 is not None, "Product2 not found in the receipt"
    assert prod2.name == product2.name, f"Expected name {product2.name}, got {prod2.name}"
    assert prod2.barcode == product2.barcode, f"Expected barcode {product2.barcode}, got {prod2.barcode}"
    assert prod2.price == product2.price, f"Expected price {product2.price}, got {prod2.price}"
