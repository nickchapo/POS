import uuid

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from app.infra.fastapi.dependables import get_product_repository
from app.infra.fastapi.products import router
from app.infra.sqlite.products import ProductSQLite


@pytest.fixture
def repo() -> ProductSQLite:
    repository = ProductSQLite(":memory:")
    repository.clear()
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


def test_create_product_success(client: TestClient) -> None:
    data = {"name": "New Product", "barcode": "abc123", "price": 9.99}
    response = client.post("/products", json=data)
    assert response.status_code == 201
    json_data = response.json()
    assert json_data["name"] == "New Product"
    assert json_data["barcode"] == "abc123"
    assert json_data["price"] == 9.99
    try:
        uuid.UUID(json_data["id"])
    except ValueError:
        pytest.fail("Invalid UUID returned")


def test_create_product_conflict(client: TestClient) -> None:
    data = {"name": "Conflict Product", "barcode": "conflict123", "price": 19.99}
    response = client.post("/products", json=data)
    assert response.status_code == 201

    data_conflict = {
        "name": "Conflict Product",
        "barcode": "unique_barcode",
        "price": 29.99,
    }
    response_conflict = client.post("/products", json=data_conflict)
    assert response_conflict.status_code == 409

    data_conflict_barcode = {
        "name": "Unique Product",
        "barcode": "conflict123",
        "price": 29.99,
    }
    response_conflict_barcode = client.post("/products", json=data_conflict_barcode)
    assert response_conflict_barcode.status_code == 409


def test_get_product_success(client: TestClient) -> None:
    data = {"name": "Get Product", "barcode": "get123", "price": 12.34}
    create_resp = client.post("/products", json=data)
    assert create_resp.status_code == 201
    product_id = create_resp.json()["id"]

    get_resp = client.get(f"/products/{product_id}")
    assert get_resp.status_code == 200
    json_data = get_resp.json()
    assert json_data["id"] == product_id
    assert json_data["name"] == "Get Product"
    assert json_data["barcode"] == "get123"
    assert json_data["price"] == 12.34


def test_get_product_not_found(client: TestClient) -> None:
    non_existent_id = str(uuid.uuid4())
    response = client.get(f"/products/{non_existent_id}")
    assert response.status_code == 404


def test_list_products(client: TestClient) -> None:
    client.post(
        "/products", json={"name": "List Product 1", "barcode": "list1", "price": 5.55}
    )
    client.post(
        "/products", json={"name": "List Product 2", "barcode": "list2", "price": 6.66}
    )
    response = client.get("/products")
    assert response.status_code == 200
    json_data = response.json()
    assert "products" in json_data
    assert len(json_data["products"]) == 2


def test_update_product_success(client: TestClient) -> None:
    data = {"name": "Update Product", "barcode": "update123", "price": 10.0}
    create_resp = client.post("/products", json=data)
    assert create_resp.status_code == 201
    product_id = create_resp.json()["id"]

    update_data = {"price": 15.0}
    patch_resp = client.patch(f"/products/{product_id}", json=update_data)
    assert patch_resp.status_code == 200

    get_resp = client.get(f"/products/{product_id}")
    assert get_resp.status_code == 200
    assert get_resp.json()["price"] == 15.0


def test_update_product_not_found(client: TestClient) -> None:
    non_existent_id = str(uuid.uuid4())
    update_data = {"price": 20.0}
    response = client.patch(f"/products/{non_existent_id}", json=update_data)
    assert response.status_code == 404
