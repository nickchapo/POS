import sqlite3
import uuid
from datetime import datetime

import pytest

from app.infra.core.currency import Currency
from app.infra.core.repository.payments import Payment
from app.infra.core.repository.receipts import Receipt
from app.infra.sqlite.payments import PaymentSqlLite
from app.infra.sqlite.products import ProductSQLite
from app.infra.sqlite.receipts import ReceiptSqlLite


@pytest.fixture(scope="function")
def connection() -> sqlite3.Connection:
    conn = sqlite3.connect(":memory:", check_same_thread=False)
    yield conn
    conn.close()


@pytest.fixture(scope="function", autouse=True)
def init_db(connection: sqlite3.Connection):
    ReceiptSqlLite(connection=connection)
    ProductSQLite(connection=connection)
    PaymentSqlLite(connection=connection)


@pytest.fixture
def payment_repo(connection: sqlite3.Connection) -> PaymentSqlLite:
    return PaymentSqlLite(connection=connection)


@pytest.fixture
def receipt_repo(connection: sqlite3.Connection) -> ReceiptSqlLite:
    return ReceiptSqlLite(connection=connection)


def test_add_payment(payment_repo: PaymentSqlLite):
    payment = Payment(
        id=uuid.uuid4(),
        receipt_id=uuid.uuid4(),
        amount=100.0,
        currency=Currency.USD,
        created_at=datetime.utcnow(),
    )
    added_payment = payment_repo.add(payment)
    assert added_payment.id == payment.id
    assert added_payment.amount == payment.amount
    assert added_payment.currency == payment.currency


def test_get_nonexistent_payment(payment_repo: PaymentSqlLite):
    nonexistent_id = uuid.uuid4()
    payment = payment_repo.get(nonexistent_id)
    assert payment is None


def test_get_all_payments(payment_repo: PaymentSqlLite):
    payments = []
    for _ in range(3):
        payment = Payment(
            id=uuid.uuid4(),
            receipt_id=uuid.uuid4(),
            amount=50.0,
            currency=Currency.USD,
            created_at=datetime.now(),
        )
        payment_repo.add(payment)
        payments.append(payment)
    all_payments = payment_repo.get_all()
    assert len(all_payments) == 3
    added_ids = {p.id for p in all_payments}
    for payment in payments:
        assert payment.id in added_ids


def test_receipt_has_payment(
    payment_repo: PaymentSqlLite, receipt_repo: ReceiptSqlLite
):
    receipt = receipt_repo.add(Receipt())
    receipt_id = receipt.id

    assert payment_repo.receipt_has_payment(receipt_id) is False

    payment = Payment(
        id=uuid.uuid4(),
        receipt_id=receipt_id,
        amount=75.0,
        currency=Currency.USD,
        created_at=datetime.now(),
    )
    payment_repo.add(payment)
    assert payment_repo.receipt_has_payment(receipt_id) is True
