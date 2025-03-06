import sqlite3
from uuid import UUID

from app.infra.core.entity.receipt import Receipt
from app.infra.core.errors import DoesNotExistError
from app.infra.core.repository.receipt_repository import ReceiptRepository


class ReceiptSqlLite(ReceiptRepository):
    def __init__(self, db_name: str):
        self.connection = sqlite3.connect(db_name, check_same_thread=False)
        self.connection.row_factory = sqlite3.Row
        self._initialize_table()

    def _initialize_table(self) -> None:
        with self.connection:
            self.connection.execute(
                """
                CREATE TABLE IF NOT EXISTS receipts (
                    id TEXT PRIMARY KEY
                )
                """
            )

    def get(self, receipt_id: UUID) -> Receipt:
        with self.connection:
            cursor = self.connection.execute(
                "SELECT id FROM receipts WHERE id = ?",
                (str(receipt_id),)
            )
            row = cursor.fetchone()
            if row is None:
                raise DoesNotExistError("Receipt", "id", str(receipt_id))
            return Receipt(id=UUID(row["id"]))

    def add(self, receipt: Receipt) -> None:
        with self.connection:
            self.connection.execute(
                "INSERT INTO receipts (id) VALUES (?)",
                (str(receipt.id),)
            )

    def clear(self) -> None:
        with self.connection:
            self.connection.execute("DELETE FROM receipts")
