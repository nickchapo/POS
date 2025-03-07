from uuid import UUID

from pydantic import BaseModel


class AddReceiptProductRequest(BaseModel):
    product_id: UUID
