from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Optional, Protocol
from uuid import UUID, uuid4


@dataclass
class Shift:
    id: UUID = field(default_factory=uuid4)
    open_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    closed_at: Optional[datetime] = None


class ShiftRepository(Protocol):
    def open_shift(self) -> Shift:
        ...

    def close_shift(self, shift_id: UUID) -> None:
        ...

    def read(self, shift_id: UUID) -> Shift:
        ...
