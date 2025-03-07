import sqlite3
import uuid

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from app.infra.core.service.receipts import ReceiptService
from app.infra.fastapi.dependables import get_receipt_service
from app.infra.fastapi.receipts import router
from app.infra.sqlite.products import ProductSQLite
from app.infra.sqlite.receipts import ReceiptSqlLite


@pytest.fixture(scope="function")
def connection() -> sqlite3.Connection:
    conn = sqlite3.connect(":memory:", check_same_thread=False)
    yield conn
    conn.close()


@pytest.fixture
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


@pytest.fixture
def app(receipt_service: ReceiptService) -> FastAPI:
    app = FastAPI()
    app.dependency_overrides[get_receipt_service] = lambda: receipt_service
    app.include_router(router)
    return app


@pytest.fixture
def client(app: FastAPI) -> TestClient:
    return TestClient(app)


def test_create_receipt(client: TestClient) -> None:
    response = client.post("/receipts")
    assert response.status_code == 201
    receipt_id = response.json().get("receipt_id")
    assert receipt_id is not None


def test_get_receipt(client: TestClient) -> None:
    create_response = client.post("/receipts")
    receipt_id = create_response.json()["receipt_id"]

    get_response = client.get(f"/receipts/{receipt_id}")
    assert get_response.status_code == 200
    assert get_response.json()["receipt_id"] == str(receipt_id)


def test_get_receipt_not_found(client: TestClient) -> None:
    non_existent_id = str(uuid.uuid4())
    response = client.get(f"/receipts/{non_existent_id}")
    assert response.status_code == 404
