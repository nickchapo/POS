import uuid

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from app.infra.core.entity.receipt import Receipt
from app.infra.core.errors import DoesNotExistError
from app.infra.fastapi.dependables import get_receipt_repository
from app.infra.fastapi.receipts import router
from app.infra.sqlite.receipt_repository import ReceiptSqlLite


@pytest.fixture
def repo() -> ReceiptSqlLite:
    repository = ReceiptSqlLite(":memory:")
    return repository


@pytest.fixture
def app(repo: ReceiptSqlLite) -> FastAPI:
    app = FastAPI()

    def get_test_repo() -> ReceiptSqlLite:
        return repo

    app.dependency_overrides[get_receipt_repository] = get_test_repo
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
