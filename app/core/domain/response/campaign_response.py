from datetime import datetime
from typing import List, Optional
from uuid import UUID

from pydantic import BaseModel


class campaign_response(BaseModel):
    id: int
    campaign_type: str
    active: bool
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    discount_percentage: Optional[float] = None
    product_id: Optional[UUID] = None
    min_total: Optional[float] = None
    buy_quantity: Optional[int] = None
    free_quantity: Optional[int] = None
    combo_products: Optional[List[UUID]] = None
    combo_discount: Optional[float] = None
