import sqlite3
from dataclasses import dataclass
from datetime import datetime
from typing import List, Optional
from uuid import UUID

from app.infra.core.currency import Currency
from app.infra.core.repository.payments import Payment, PaymentRepository


@dataclass
class PaymentSqlLite(PaymentRepository):
    db_name: Optional[str] = None
    connection: Optional[sqlite3.Connection] = None

    def __post_init__(self):
        if self.connection is None:
            self.connection = sqlite3.connect(self.db_name, check_same_thread=False)
        self.connection.row_factory = sqlite3.Row
        self._initialize_table()

    def _initialize_table(self) -> None:
        with self.connection:
            self.connection.execute(
                """
                CREATE TABLE IF NOT EXISTS payments (
                    id TEXT PRIMARY KEY,
                    receipt_id TEXT NOT NULL,
                    amount REAL NOT NULL,
                    currency TEXT NOT NULL,
                    created_at TEXT NOT NULL,
                    FOREIGN KEY (receipt_id) REFERENCES receipts (id)
                )
                """
            )

    def add(self, payment: Payment) -> Payment:
        with self.connection:
            self.connection.execute(
                """
                INSERT INTO payments (id, receipt_id, amount, currency, created_at)
                VALUES (?, ?, ?, ?, ?)
                """,
                (
                    str(payment.id),
                    str(payment.receipt_id),
                    payment.amount,
                    payment.currency.value,
                    payment.created_at.isoformat()
                )
            )
        return self.get(payment.id)

    def get(self, payment_id: UUID) -> Payment | None:
        query = "SELECT * FROM payments WHERE id = ?"
        cursor = self.connection.execute(query, (str(payment_id),))
        row = cursor.fetchone()

        if not row:
            return None

        return self._row_to_payment(row)

    def get_all(self) -> List[Payment]:
        query = "SELECT * FROM payments"
        cursor = self.connection.execute(query)
        rows = cursor.fetchall()

        return [self._row_to_payment(row) for row in rows]

    def receipt_has_payment(self, receipt_id: UUID) -> bool:
        query = "SELECT 1 FROM payments WHERE receipt_id = ? LIMIT 1"
        cursor = self.connection.execute(query, (str(receipt_id),))
        return cursor.fetchone() is not None

    def _row_to_payment(self, row) -> Payment:
        return Payment(
            id=UUID(row["id"]),
            receipt_id=UUID(row["receipt_id"]),
            amount=row["amount"],
            currency=Currency(row["currency"]),
            created_at=datetime.fromisoformat(row["created_at"])
        )
