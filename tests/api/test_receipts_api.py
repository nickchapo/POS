import sqlite3
import uuid

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from app.infra.core.service.receipts import ReceiptService
from app.infra.fastapi.dependables import get_receipt_service, get_product_repository
from app.infra.fastapi.receipts import router as receipts_router
from app.infra.fastapi.products import router as products_router
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
def receipt_service(
    receipt_repo: ReceiptSqlLite, product_repo: ProductSQLite
) -> ReceiptService:
    return ReceiptService(
        receipt_repository=receipt_repo, product_repository=product_repo
    )


@pytest.fixture
def app(receipt_service: ReceiptService, product_repo: ProductSQLite) -> FastAPI:
    app = FastAPI()
    app.dependency_overrides[get_receipt_service] = lambda: receipt_service
    app.dependency_overrides[get_product_repository] = lambda: product_repo
    app.include_router(receipts_router)
    app.include_router(products_router)
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


def test_add_product_to_receipt_success(client: TestClient) -> None:
    receipt_response = client.post("/receipts")
    assert receipt_response.status_code == 201
    receipt_id = receipt_response.json()["receipt_id"]

    product_data_1 = {"name": "Product1", "barcode": "1test123", "price": 10.99}
    product_response_1 = client.post("/products", json=product_data_1)
    assert product_response_1.status_code == 201

    product_data_2 = {"name": "Product2", "barcode": "2test123", "price": 20.99}
    product_response_2 = client.post("/products", json=product_data_2)
    assert product_response_2.status_code == 201

    product_id_1 = product_response_1.json()["id"]
    product_id_2 = product_response_2.json()["id"]

    add_response_1 = client.post(
        f"/receipts/{receipt_id}/products", json={"product_id": product_id_1}
    )
    assert add_response_1.status_code == 200
    add_response_2 = client.post(
        f"/receipts/{receipt_id}/products", json={"product_id": product_id_2}
    )
    assert add_response_2.status_code == 200

    updated_receipt_json = add_response_2.json()
    assert updated_receipt_json["receipt_id"] == receipt_id
    assert "products" in updated_receipt_json
    assert len(updated_receipt_json["products"]) == 2

    product_1 = next(
        (
            prod
            for prod in updated_receipt_json["products"]
            if prod["name"] == "Product1"
        ),
        None,
    )
    product_2 = next(
        (
            prod
            for prod in updated_receipt_json["products"]
            if prod["name"] == "Product2"
        ),
        None,
    )
    assert product_1 is not None
    assert product_2 is not None

    assert product_1["id"]
    assert product_1["barcode"] == "1test123"
    assert product_1["price"] == 10.99
    assert product_2["id"]
    assert product_2["barcode"] == "2test123"
    assert product_2["price"] == 20.99


def test_add_nonexisting_product_to_receipt(client: TestClient) -> None:
    receipt_response = client.post("/receipts")
    assert receipt_response.status_code == 201
    receipt_id = receipt_response.json()["receipt_id"]

    add_response = client.post(
        f"/receipts/{receipt_id}/products", json={"product_id": str(uuid.uuid4())}
    )
    assert add_response.status_code == 404


def test_add_duplicate_product_to_receipt(client: TestClient) -> None:
    receipt_response = client.post("/receipts")
    assert receipt_response.status_code == 201
    receipt_id = receipt_response.json()["receipt_id"]

    product_data_1 = {"name": "Product1", "barcode": "1test123", "price": 10.99}
    product_response_1 = client.post("/products", json=product_data_1)
    assert product_response_1.status_code == 201

    product_id_1 = product_response_1.json()["id"]

    add_response_1 = client.post(
        f"/receipts/{receipt_id}/products", json={"product_id": product_id_1}
    )
    assert add_response_1.status_code == 200
    add_response_2 = client.post(
        f"/receipts/{receipt_id}/products", json={"product_id": product_id_1}
    )
    print(add_response_2.json())
    assert add_response_2.status_code == 409
