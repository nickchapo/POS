import sqlite3
from dataclasses import dataclass
from typing import Optional
from uuid import UUID

from app.core.errors import DoesNotExistError, ExistsError
from app.core.repository.products import Product, ProductRepository


@dataclass
class ProductSQLite(ProductRepository):
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
                CREATE TABLE IF NOT EXISTS products (
                    id TEXT PRIMARY KEY,
                    name TEXT UNIQUE,
                    barcode TEXT UNIQUE,
                    price REAL,
                    receipt_id TEXT,
                    FOREIGN KEY (receipt_id) REFERENCES receipts (id)
                )
                """
            )

    def exists(self, product_id) -> bool:
        with self.connection:
            with self.connection:
                cursor = self.connection.execute(
                    "SELECT 1 FROM products WHERE id = ?", (str(product_id),)
                )
                return cursor.fetchone() is not None

    def add(self, product: Product) -> None:
        try:
            with self.connection:
                self.connection.execute(
                    "INSERT INTO products (id, name, barcode, price)"
                    " VALUES (?, ?, ?, ?)",
                    (str(product.id), product.name, product.barcode, product.price),
                )
        except sqlite3.IntegrityError as e:
            existing = self.read_list()
            if any(p.name == product.name for p in existing):
                raise ExistsError("Product", "name", product.name)
            if any(p.barcode == product.barcode for p in existing):
                raise ExistsError("Product", "barcode", product.barcode)
            raise e

    def read(self, product_id: UUID) -> Product:
        cursor = self.connection.execute(
            "SELECT id, name, barcode, price FROM products WHERE id=?",
            (str(product_id),),
        )
        row = cursor.fetchone()
        cursor.close()
        if row:
            return Product(
                id=UUID(row["id"]),
                name=row["name"],
                barcode=row["barcode"],
                price=row["price"],
            )
        else:
            raise DoesNotExistError("Product", "id", str(product_id))

    def read_list(self) -> list[Product]:
        cursor = self.connection.execute(
            "SELECT id, name, barcode, price FROM products"
        )
        rows = cursor.fetchall()
        cursor.close()
        return [
            Product(
                id=UUID(row["id"]),
                name=row["name"],
                barcode=row["barcode"],
                price=row["price"],
            )
            for row in rows
        ]

    def update_price(self, product_id: UUID, price: float) -> None:
        self.read(product_id)
        with self.connection:
            self.connection.execute(
                "UPDATE products SET price=? WHERE id=?",
                (price, str(product_id)),
            )

    def update_receipt_id(self, product_id: UUID, receipt_id: UUID) -> None:
        self.read(product_id)
        with self.connection:
            self.connection.execute(
                "UPDATE products SET receipt_id=? WHERE id=?",
                (str(receipt_id), str(product_id)),
            )

    def clear(self) -> None:
        with self.connection:
            self.connection.execute("DELETE FROM products")
