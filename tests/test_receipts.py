import sqlite3
import uuid

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from app.infra.core.entity.receipt import Receipt
from app.infra.core.errors import DoesNotExistError
from app.infra.core.products import Product
from app.infra.fastapi.dependables import get_receipt_repository, get_product_repository
from app.infra.fastapi.receipts import router
from app.infra.sqlite.products import ProductSQLite
from app.infra.sqlite.receipt_repository import ReceiptSqlLite


@pytest.fixture
def product_repo() -> ProductSQLite:
    repository = ProductSQLite(":memory:")
    return repository


@pytest.fixture
def receipt_repo(product_repo: ProductSQLite) -> ReceiptSqlLite:
    repository = ReceiptSqlLite(":memory:", product_repo=product_repo)
    return repository


@pytest.fixture
def app(receipt_repo: ReceiptSqlLite, product_repo: ProductSQLite) -> FastAPI:
    app = FastAPI()
    app.dependency_overrides[get_receipt_repository] = lambda: receipt_repo
    app.dependency_overrides[get_product_repository] = lambda: product_repo
    app.include_router(router)
    return app


@pytest.fixture
def client(app: FastAPI) -> TestClient:
    return TestClient(app)


# repo tests

def test_add_and_get_receipt(receipt_repo: ReceiptSqlLite):
    receipt = Receipt()
    receipt_repo.add(receipt)
    retrieved = receipt_repo.get(receipt.id)
    assert retrieved.id == receipt.id


def test_get_nonexistent_receipt(receipt_repo: ReceiptSqlLite):
    nonexistent_id = uuid.uuid4()

    with pytest.raises(DoesNotExistError):
        receipt_repo.get(nonexistent_id)


def test_clear_receipts(receipt_repo: ReceiptSqlLite):
    receipts = [Receipt() for _ in range(3)]
    for receipt in receipts:
        receipt_repo.add(receipt)

    receipt_repo.clear()

    for receipt in receipts:
        with pytest.raises(DoesNotExistError):
            receipt_repo.get(receipt.id)


def test_add_products_and_get_receipt(receipt_repo: ReceiptSqlLite, product_repo: ProductSQLite):
    receipt = Receipt()
    receipt_repo.add(receipt)

    product1 = Product(id=uuid.uuid4(), name="Product1", barcode="barcode1", price=10.0)
    product2 = Product(id=uuid.uuid4(), name="Product2", barcode="barcode2", price=20.0)
    product_repo.add(product1)
    product_repo.add(product2)

    receipt_repo.add_product(receipt.id, product1.id)
    receipt_repo.add_product(receipt.id, product2.id)

    retrieved = receipt_repo.get(receipt.id)
    product_ids = {p.id for p in retrieved.products}
    assert len(retrieved.products) == 2
    assert product1.id in product_ids
    assert product2.id in product_ids


def test_add_duplicate_product(receipt_repo: ReceiptSqlLite, product_repo: ProductSQLite):
    receipt = Receipt()
    receipt_repo.add(receipt)

    product = Product(id=uuid.uuid4(), name="Product", barcode="barcode", price=10.0)
    product_repo.add(product)

    receipt_repo.add_product(receipt.id, product.id)

    with pytest.raises(sqlite3.IntegrityError):
        receipt_repo.add_product(receipt.id, product.id)


def test_add_nonexisting_product(receipt_repo: ReceiptSqlLite):
    receipt = Receipt()
    receipt_repo.add(receipt)

    id = uuid.uuid4()

    with pytest.raises(DoesNotExistError):
        receipt_repo.add_product(receipt.id, id)

# api tests

def test_create_receipt_endpoint(client: TestClient) -> None:
    response = client.post("/receipts")
    assert response.status_code == 201
    data = response.json()
    assert "id" in data


def test_get_receipt_endpoint(client: TestClient) -> None:
    create_resp = client.post("/receipts")
    assert create_resp.status_code == 201
    receipt_data = create_resp.json()
    receipt_id = receipt_data["id"]

    get_resp = client.get(f"/receipts/{receipt_id}")
    assert get_resp.status_code == 200
    retrieved = get_resp.json()
    assert retrieved["id"] == receipt_id


def test_get_receipt_not_found(client: TestClient) -> None:
    non_existent_id = str(uuid.uuid4())
    response = client.get(f"/receipts/{non_existent_id}")
    assert response.status_code == 404
