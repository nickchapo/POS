import uuid

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from app.infra.fastapi.dependables import get_receipt_repository, get_product_repository
from app.infra.fastapi.receipts import router
from app.infra.sqlite.products import ProductSQLite
from app.infra.sqlite.receipts import ReceiptSqlLite


@pytest.fixture
def product_repo() -> ProductSQLite:
    repository = ProductSQLite(":memory:")
    return repository


@pytest.fixture
def receipt_repo() -> ReceiptSqlLite:
    repository = ReceiptSqlLite(":memory:")
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
