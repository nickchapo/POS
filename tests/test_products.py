import uuid

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from app.infra.core.errors import DoesNotExistError, ExistsError
from app.infra.core.products import Product
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


# repo tests

def test_add_and_read_product(repo: ProductSQLite) -> None:
    product_id = uuid.uuid4()
    product = Product(id=product_id, name="Test Product", barcode="123456", price=10.0)
    repo.add(product)
    retrieved = repo.read(product_id)
    assert retrieved.id == product.id
    assert retrieved.name == product.name
    assert retrieved.barcode == product.barcode
    assert retrieved.price == product.price


def test_add_duplicate_name(repo: ProductSQLite) -> None:
    product1 = Product(id=uuid.uuid4(), name="prod", barcode="111", price=5.0)
    product2 = Product(id=uuid.uuid4(), name="prod", barcode="222", price=6.0)
    repo.add(product1)
    with pytest.raises(ExistsError) as excinfo:
        repo.add(product2)
    assert "name" in str(excinfo.value)


def test_add_duplicate_barcode(repo: ProductSQLite) -> None:
    product1 = Product(id=uuid.uuid4(), name="Product1", barcode="dup", price=5.0)
    product2 = Product(id=uuid.uuid4(), name="Product2", barcode="dup", price=6.0)
    repo.add(product1)
    with pytest.raises(ExistsError) as excinfo:
        repo.add(product2)
    assert "barcode" in str(excinfo.value)


def test_read_nonexistent_product(repo: ProductSQLite) -> None:
    non_existent_id = uuid.uuid4()
    with pytest.raises(DoesNotExistError):
        repo.read(non_existent_id)


def test_update_price(repo: ProductSQLite) -> None:
    product_id = uuid.uuid4()
    product = Product(id=product_id, name="Product", barcode="123", price=10.0)
    repo.add(product)
    new_price = 15.0
    repo.update_price(product_id, new_price)
    updated_product = repo.read(product_id)
    assert updated_product.price == new_price


def test_list_and_clear_products(repo: ProductSQLite) -> None:
    product1 = Product(id=uuid.uuid4(), name="Product1", barcode="barcode1", price=10.0)
    product2 = Product(id=uuid.uuid4(), name="Product2", barcode="barcode2", price=20.0)
    repo.add(product1)
    repo.add(product2)
    products = repo.read_list()
    assert len(products) == 2
    repo.clear()
    products_after_clear = repo.read_list()
    assert len(products_after_clear) == 0


# api tests

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

    data_conflict = {"name": "Conflict Product", "barcode": "unique_barcode",
                     "price": 29.99}
    response_conflict = client.post("/products", json=data_conflict)
    assert response_conflict.status_code == 409

    data_conflict_barcode = {"name": "Unique Product", "barcode": "conflict123",
                             "price": 29.99}
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
    client.post("/products",
                json={"name": "List Product 1", "barcode": "list1", "price": 5.55})
    client.post("/products",
                json={"name": "List Product 2", "barcode": "list2", "price": 6.66})
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
