from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel


class ShiftResponse(BaseModel):
    id: UUID
    open_at: datetime
    closed_at: Optional[datetime] = None
