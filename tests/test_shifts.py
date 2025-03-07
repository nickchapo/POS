import uuid
from datetime import datetime
from uuid import UUID

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from app.infra.core.errors import DoesNotExistError, ShiftClosedError
from app.infra.fastapi.dependables import get_shift_repository
from app.infra.fastapi.shifts import router
from app.infra.sqlite.shifts import ShiftSQLite


@pytest.fixture
def repo() -> ShiftSQLite:
    repository = ShiftSQLite(":memory:")
    return repository


def test_open_shift(repo: ShiftSQLite) -> None:
    shift = repo.open_shift()
    assert isinstance(shift.id, UUID)
    assert isinstance(shift.open_at, datetime)
    assert shift.closed_at is None

    shift_from_db = repo.read(shift.id)
    assert shift_from_db.id == shift.id
    assert shift_from_db.open_at == shift.open_at
    assert shift_from_db.closed_at is None


def test_close_shift(repo: ShiftSQLite) -> None:
    shift = repo.open_shift()
    repo.close_shift(shift.id)
    closed_shift = repo.read(shift.id)
    assert closed_shift.closed_at is not None

    with pytest.raises(ShiftClosedError):
        repo.close_shift(shift.id)


def test_read_nonexistent_shift(repo: ShiftSQLite) -> None:
    non_existent_id = uuid.uuid4()
    with pytest.raises(DoesNotExistError):
        repo.read(non_existent_id)


# endpoints


@pytest.fixture
def app() -> FastAPI:
    app = FastAPI()
    test_repo = ShiftSQLite(":memory:")

    def get_test_repo() -> ShiftSQLite:
        return test_repo

    app.dependency_overrides[get_shift_repository] = get_test_repo
    app.include_router(router)
    return app


@pytest.fixture
def client(app: FastAPI) -> TestClient:
    return TestClient(app)


def test_open_shift_endpoint(client: TestClient) -> None:
    response = client.post("/shifts")
    assert response.status_code == 201
    data = response.json()
    assert "id" in data
    assert "open_at" in data
    assert data["closed_at"] is None


def test_get_shift_endpoint(client: TestClient) -> None:
    open_resp = client.post("/shifts")
    assert open_resp.status_code == 201
    shift_data = open_resp.json()
    shift_id = shift_data["id"]

    get_resp = client.get(f"/shifts/{shift_id}")
    assert get_resp.status_code == 200
    retrieved = get_resp.json()
    assert retrieved["id"] == shift_id
    assert retrieved["open_at"] == shift_data["open_at"]
    assert retrieved["closed_at"] == shift_data["closed_at"]


def test_get_shift_not_found(client: TestClient) -> None:
    non_existent_id = str(uuid.uuid4())
    response = client.get(f"/shifts/{non_existent_id}")
    assert response.status_code == 404


def test_close_shift_endpoint(client: TestClient) -> None:
    open_resp = client.post("/shifts")
    assert open_resp.status_code == 201
    shift_data = open_resp.json()
    shift_id = shift_data["id"]

    close_resp = client.patch(f"/shifts/{shift_id}/close")
    assert close_resp.status_code == 200
    closed_data = close_resp.json()
    assert closed_data["id"] == shift_id
    assert closed_data["closed_at"] is not None


def test_close_shift_already_closed(client: TestClient) -> None:
    open_resp = client.post("/shifts")
    assert open_resp.status_code == 201
    shift_id = open_resp.json()["id"]

    first_close = client.patch(f"/shifts/{shift_id}/close")
    assert first_close.status_code == 200

    second_close = client.patch(f"/shifts/{shift_id}/close")
    assert second_close.status_code == 400


def test_close_shift_not_found(client: TestClient) -> None:
    non_existent_id = str(uuid.uuid4())
    response = client.patch(f"/shifts/{non_existent_id}/close")
    assert response.status_code == 404
