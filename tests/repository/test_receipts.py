import sqlite3
import uuid

import pytest

from app.infra.sqlite.products import ProductSQLite
from app.infra.sqlite.receipt_product import ReceiptProductSqlLite
from app.infra.sqlite.receipts import ReceiptSqlLite, Receipt


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


def test_get_with_products(receipt_repo: ReceiptSqlLite, receipt_product_repo: ReceiptProductSqlLite):
    receipt = Receipt()
    receipt_repo.add(receipt)

    product_id_1 = uuid.uuid4()
    product_id_2 = uuid.uuid4()
    receipt_product_repo.add_receipt_product(receipt.id, product_id_1)
    receipt_product_repo.add_receipt_product(receipt.id, product_id_2)

    retrieved = receipt_repo.get(receipt.id)
    assert len(retrieved.product_ids) == 2
    assert product_id_1 in retrieved.product_ids
    assert product_id_1 in retrieved.product_ids
