import sqlite3
import uuid

import pytest

from app.infra.core.errors import DoesNotExistError
from app.infra.core.repository.products import Product
from app.infra.core.service.receipts import ReceiptService
from app.infra.sqlite.products import ProductSQLite
from app.infra.sqlite.receipts import ReceiptSqlLite


@pytest.fixture(scope="function")
def connection() -> sqlite3.Connection:
    conn = sqlite3.connect(":memory:", check_same_thread=False)
    yield conn
    conn.close()


@pytest.fixture(scope="function", autouse=True)
def init_db(connection: sqlite3.Connection):
    ReceiptSqlLite(connection=connection)
    ProductSQLite(connection=connection)


@pytest.fixture
def receipt_repo(connection: sqlite3.Connection) -> ReceiptSqlLite:
    repository = ReceiptSqlLite(connection=connection)
    return repository


@pytest.fixture
def product_repo(connection: sqlite3.Connection) -> ProductSQLite:
    repository = ProductSQLite(connection=connection)
    return repository


@pytest.fixture
def receipt_service(receipt_repo: ReceiptSqlLite, product_repo: ProductSQLite) -> ReceiptService:
    return ReceiptService(receipt_repository=receipt_repo, product_repository=product_repo)


def test_get_receipt_not_exist(receipt_service: ReceiptService):
    non_existent_id = uuid.uuid4()
    with pytest.raises(DoesNotExistError):
        receipt_service.get_receipt(non_existent_id)


def test_add_receipt(receipt_service: ReceiptService):
    receipt_response = receipt_service.add_receipt()
    assert isinstance(receipt_response.receipt_id, uuid.UUID)
    assert receipt_response.products == []


def test_add_product_success(receipt_service: ReceiptService, product_repo: ProductSQLite):
    receipt_response = receipt_service.add_receipt()
    receipt_id = receipt_response.receipt_id

    product = Product(id=uuid.uuid4(), name="Product", barcode="Barcode", price=99.99)
    product_repo.add(product)

    updated_receipt_response = receipt_service.add_product(receipt_id, product.id)
    product_ids = [p.id for p in updated_receipt_response.products]
    assert product.id in product_ids


def test_add_product_nonexistent_receipt(receipt_service: ReceiptService, product_repo: ProductSQLite):
    product = Product(id=uuid.uuid4(), name="Product", barcode="Barcode", price=99.99)
    product_repo.add(product)

    non_existent_receipt_id = uuid.uuid4()
    with pytest.raises(DoesNotExistError):
        receipt_service.add_product(non_existent_receipt_id, product.id)


def test_add_product_nonexistent_product(receipt_service: ReceiptService):
    receipt_response = receipt_service.add_receipt()
    receipt_id = receipt_response.receipt_id

    non_existent_product_id = uuid.uuid4()
    with pytest.raises(DoesNotExistError):
        receipt_service.add_product(receipt_id, non_existent_product_id)
