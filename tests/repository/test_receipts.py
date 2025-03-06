import sqlite3
import uuid

import pytest

from app.infra.core.repository.products import Product
from app.infra.core.repository.receipts import Receipt
from app.infra.sqlite.products import ProductSQLite
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


@pytest.fixture
def receipt_repo(connection: sqlite3.Connection) -> ReceiptSqlLite:
    repository = ReceiptSqlLite(connection=connection)
    return repository


@pytest.fixture
def product_repo(connection: sqlite3.Connection) -> ProductSQLite:
    repository = ProductSQLite(connection=connection)
    return repository


def test_receipt_exists_true(receipt_repo: ReceiptSqlLite):
    receipt = Receipt()
    receipt_repo.add(receipt)
    assert receipt_repo.exists(receipt.id) is True


def test_receipt_exists_false(receipt_repo: ReceiptSqlLite):
    non_existing_id = uuid.uuid4()
    assert receipt_repo.exists(non_existing_id) is False


def test_get_nonexistent_receipt(receipt_repo: ReceiptSqlLite):
    nonexistent_id = uuid.uuid4()
    receipt = receipt_repo.get(nonexistent_id)
    assert receipt is None


def test_add_and_get_receipt(receipt_repo: ReceiptSqlLite):
    receipt = Receipt()
    receipt_repo.add(receipt)
    retrieved = receipt_repo.get(receipt.id)
    assert retrieved.id == receipt.id


def test_clear_receipts(receipt_repo: ReceiptSqlLite):
    receipts = [Receipt() for _ in range(3)]
    for receipt in receipts:
        receipt_repo.add(receipt)

    receipt_repo.clear()

    for receipt in receipts:
        retrieved = receipt_repo.get(receipt.id)
        assert retrieved is None

def test_get_with_products(receipt_repo: ReceiptSqlLite, product_repo: ProductSQLite):
    receipt = Receipt()
    receipt_repo.add(receipt)

    product1 = Product(id=uuid.uuid4(), name="Product1", barcode="barcode1", price=10.0)
    product2 = Product(id=uuid.uuid4(), name="Product2", barcode="barcode2", price=20.0)
    product_repo.add(product1)
    product_repo.add(product2)

    product_repo.update_receipt_id(product1.id, receipt.id)
    product_repo.update_receipt_id(product2.id, receipt.id)

    retrieved = receipt_repo.get(receipt.id)

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
