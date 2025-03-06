import sqlite3
from dataclasses import dataclass, field
from typing import Optional
from uuid import UUID

from app.infra.core.receipt_product import ReceiptProductRepository


@dataclass
class ReceiptProductSqlLite(ReceiptProductRepository):
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
                CREATE TABLE IF NOT EXISTS receipt_products (
                    receipt_id TEXT,
                    product_id TEXT,
                    PRIMARY KEY (receipt_id, product_id),
                    FOREIGN KEY (receipt_id) REFERENCES receipts (id),
                    FOREIGN KEY (product_id) REFERENCES products (id)
                )
                """
            )

    def add_receipt_product(self, receipt_id: UUID, product_id: UUID) -> None:
        with self.connection:
            self.connection.execute(
                "INSERT INTO receipt_products (receipt_id, product_id) VALUES (?, ?)",
                (str(receipt_id), str(product_id))
            )
