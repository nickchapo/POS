import sqlite3
from datetime import datetime, timezone
from uuid import UUID

from app.infra.core.errors import DoesNotExistError, ShiftClosedError
from app.infra.core.repository.shifts import ShiftRepository, Shift


class ShiftSQLite(ShiftRepository):
    def __init__(self, db_name: str):
        self.connection = sqlite3.connect(db_name, check_same_thread=False)
        self.connection.row_factory = sqlite3.Row
        self._initialize_table()

    def _initialize_table(self) -> None:
        with self.connection:
            self.connection.execute(
                """
                CREATE TABLE IF NOT EXISTS shifts (
                    id TEXT PRIMARY KEY,
                    open_at TEXT NOT NULL,
                    closed_at TEXT
                )
                """
            )

    def open_shift(self) -> Shift:
        new_shift = Shift(open_at=datetime.now(timezone.utc))
        with self.connection:
            self.connection.execute(
                "INSERT INTO shifts (id, open_at, closed_at) VALUES (?, ?, ?)",
                (str(new_shift.id), new_shift.open_at.isoformat(), None),
            )
        return new_shift

    def close_shift(self, shift_id: UUID) -> None:
        shift = self.read(shift_id)
        if shift.closed_at is not None:
            raise ShiftClosedError(str(shift_id))
        now = datetime.now(timezone.utc)
        with self.connection:
            self.connection.execute(
                "UPDATE shifts SET closed_at = ? WHERE id = ?",
                (now.isoformat(), str(shift_id)),
            )

    def read(self, shift_id: UUID) -> Shift:
        cursor = self.connection.execute(
            "SELECT id, open_at, closed_at FROM shifts WHERE id = ?",
            (str(shift_id),),
        )
        row = cursor.fetchone()
        cursor.close()
        if row:
            return Shift(
                id=UUID(row["id"]),
                open_at=datetime.fromisoformat(row["open_at"]),
                closed_at=datetime.fromisoformat(row["closed_at"]) if row[
                    "closed_at"] else None,
            )
        else:
            raise DoesNotExistError("Shift", "id", str(shift_id))
