import sqlite3
from dataclasses import dataclass, field
from uuid import UUID

from app.infra.core.errors import DoesNotExistError
from app.infra.core.products import ProductRepository
from app.infra.core.receipts import ReceiptRepository, Receipt


@dataclass
class ReceiptSqlLite(ReceiptRepository):
    db_name: str
    connection: sqlite3.Connection = field(init=False)
    product_repo: ProductRepository

    def __post_init__(self):
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
            self.connection.execute(
                """
                CREATE TABLE IF NOT EXISTS receipt_products (
                    receipt_id TEXT,
                    product_id TEXT,
                    PRIMARY KEY (receipt_id, product_id),
                    FOREIGN KEY (receipt_id) REFERENCES receipts (id),
                    FOREIGN KEY (product_id) REFERENCES products (id)
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

            cursor_products = self.connection.execute(
                "SELECT product_id FROM receipt_products WHERE receipt_id = ?",
                (str(receipt_id),)
            )
            product_ids = [r["product_id"] for r in cursor_products.fetchall()]
            products = [self.product_repo.read(pid) for pid in product_ids]

            return Receipt(id=UUID(row["id"]), products=products)

    def add(self, receipt: Receipt) -> None:
        with self.connection:
            self.connection.execute(
                "INSERT INTO receipts (id) VALUES (?)",
                (str(receipt.id),)
            )

    def add_product(self, receipt_id: UUID, product_id: UUID) -> None:
        self.product_repo.read(product_id)
        with self.connection:
            self.connection.execute(
                "INSERT INTO receipt_products (receipt_id, product_id) VALUES (?, ?)",
                (str(receipt_id), str(product_id))
            )

    def clear(self) -> None:
        with self.connection:
            self.connection.execute("DELETE FROM receipts")
