import sqlite3
import uuid

import pytest

from app.infra.sqlite.receipt_product import ReceiptProductSqlLite


@pytest.fixture
def repo() -> ReceiptProductSqlLite:
    repository = ReceiptProductSqlLite(":memory:")
    return repository


def test_add_record(repo: ReceiptProductSqlLite):
    receipt_id = uuid.uuid4()
    product_id = uuid.uuid4()

    repo.add_receipt_product(receipt_id=receipt_id, product_id=product_id)


def test_add_duplicate_record(repo: ReceiptProductSqlLite):
    receipt_id = uuid.uuid4()
    product_id = uuid.uuid4()

    repo.add_receipt_product(receipt_id=receipt_id, product_id=product_id)

    with pytest.raises(sqlite3.IntegrityError):
        repo.add_receipt_product(receipt_id=receipt_id, product_id=product_id)
