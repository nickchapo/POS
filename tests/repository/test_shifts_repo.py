import uuid
from datetime import datetime

import pytest

from app.core.errors import DoesNotExistError, ShiftClosedError
from app.infra.sqlite.shifts import ShiftSQLite


@pytest.fixture
def repo() -> ShiftSQLite:
    return ShiftSQLite(":memory:")


def test_open_shift(repo: ShiftSQLite):
    shift = repo.open_shift()
    retrieved_shift = repo.read(shift.id)
    assert shift.id == retrieved_shift.id
    assert shift.open_at == retrieved_shift.open_at
    assert retrieved_shift.closed_at is None


def test_close_shift(repo: ShiftSQLite):
    shift = repo.open_shift()
    repo.close_shift(shift.id)
    retrieved_shift = repo.read(shift.id)
    assert retrieved_shift.closed_at is not None
    assert isinstance(retrieved_shift.closed_at, datetime)


def test_close_already_closed_shift(repo: ShiftSQLite):
    shift = repo.open_shift()
    repo.close_shift(shift.id)
    with pytest.raises(ShiftClosedError):
        repo.close_shift(shift.id)


def test_read_nonexistent_shift(repo: ShiftSQLite):
    nonexistent_id = uuid.uuid4()
    with pytest.raises(DoesNotExistError):
        repo.read(nonexistent_id)


def test_persistence_across_queries(repo: ShiftSQLite):
    shift1 = repo.open_shift()
    shift2 = repo.open_shift()
    retrieved_shift1 = repo.read(shift1.id)
    retrieved_shift2 = repo.read(shift2.id)
    assert shift1.id == retrieved_shift1.id
    assert shift2.id == retrieved_shift2.id
    assert shift1.id != shift2.id
