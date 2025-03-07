import sqlite3
from dataclasses import dataclass
from typing import Optional
from uuid import UUID

from app.infra.core.repository.products import Product
from app.infra.core.repository.receipts import ReceiptRepository, Receipt


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
                    "SELECT 1 FROM receipts WHERE id = ?", (str(receipt_id),)
                )
                return cursor.fetchone() is not None

    def get(self, receipt_id: UUID) -> Receipt | None:
        query = """
        SELECT r.id AS receipt_id, 
               p.id AS product_id, 
               p.name, 
               p.barcode, 
               p.price
        FROM receipts r
        LEFT JOIN products p ON r.id = p.receipt_id
        WHERE r.id = ?
        """
        cursor = self.connection.execute(query, (str(receipt_id),))
        rows = cursor.fetchall()
        if not rows:
            return None

        products = []
        for row in rows:
            if row["product_id"] is not None:
                product = Product(
                    id=UUID(row["product_id"]),
                    name=row["name"],
                    barcode=row["barcode"],
                    price=row["price"],
                )
                products.append(product)

        return Receipt(id=UUID(rows[0]["receipt_id"]), products=products)

    def add(self, receipt: Receipt) -> Receipt:
        with self.connection:
            self.connection.execute(
                "INSERT INTO receipts (id) VALUES (?)", (str(receipt.id),)
            )
        return self.get(receipt.id)

    def clear(self) -> None:
        with self.connection:
            self.connection.execute("DELETE FROM receipts")
