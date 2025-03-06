import sqlite3
from dataclasses import dataclass
from typing import Optional
from uuid import UUID

from app.infra.core.receipts import ReceiptRepository, Receipt


@dataclass
class ReceiptSqlLite(ReceiptRepository):
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
                CREATE TABLE IF NOT EXISTS receipts (
                    id TEXT PRIMARY KEY
                )
                """
            )

    def exists(self, receipt_id) -> bool:
        with self.connection:
            with self.connection:
                cursor = self.connection.execute(
                    "SELECT 1 FROM receipts WHERE id = ?",
                    (str(receipt_id),)
                )
                return cursor.fetchone() is not None

    def get(self, receipt_id: UUID) -> Receipt | None:
        with self.connection:
            cursor = self.connection.execute(
                """
                SELECT r.id AS receipt_id, rp.product_id
                FROM receipts r
                LEFT JOIN receipt_products rp ON r.id = rp.receipt_id
                WHERE r.id = ?
                """,
                (str(receipt_id),)
            )
            rows = cursor.fetchall()
            if not rows:
                return None

            product_ids = [row["product_id"] for row in rows if row["product_id"] is not None]
            products = [UUID(pid) for pid in product_ids]
            return Receipt(id=receipt_id, product_ids=products)

    def add(self, receipt: Receipt) -> None:
        with self.connection:
            self.connection.execute(
                "INSERT INTO receipts (id) VALUES (?)",
                (str(receipt.id),)
            )

    def clear(self) -> None:
        with self.connection:
            self.connection.execute("DELETE FROM receipts")
