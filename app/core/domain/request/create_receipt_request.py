from uuid import UUID

from pydantic import BaseModel


class CreateReceiptRequest(BaseModel):
    shift_id: UUID
