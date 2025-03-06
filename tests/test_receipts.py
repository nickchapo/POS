import uuid

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from app.infra.core.entity.receipt import Receipt
from app.infra.core.errors import DoesNotExistError
from app.infra.fastapi.dependables import get_product_repository
from app.infra.fastapi.products import router
from app.infra.sqlite.products import ProductSQLite
from app.infra.sqlite.receipt_repository import ReceiptSqlLite


@pytest.fixture
def repo() -> ReceiptSqlLite:
    repository = ReceiptSqlLite(":memory:")
    return repository


@pytest.fixture
def app(repo: ProductSQLite) -> FastAPI:
    app = FastAPI()

    def get_test_repo() -> ProductSQLite:
        return repo

    app.dependency_overrides[get_product_repository] = get_test_repo
    app.include_router(router)
    return app


@pytest.fixture
def client(app: FastAPI) -> TestClient:
    return TestClient(app)


# repo tests

def test_add_and_get_receipt(repo: ReceiptSqlLite):
    receipt = Receipt()
    repo.add(receipt)
    retrieved = repo.get(receipt.id)
    assert retrieved.id == receipt.id


def test_get_nonexistent_receipt(repo: ReceiptSqlLite):
    nonexistent_id = uuid.uuid4()

    with pytest.raises(DoesNotExistError):
        repo.get(nonexistent_id)


def test_clear_receipts(repo: ReceiptSqlLite):
    receipts = [Receipt() for _ in range(3)]
    for receipt in receipts:
        repo.add(receipt)

    repo.clear()

    for receipt in receipts:
        with pytest.raises(DoesNotExistError):
            repo.get(receipt.id)
