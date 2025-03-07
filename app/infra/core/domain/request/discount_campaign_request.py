from typing import Optional
from uuid import UUID

from ..request.base_campaign_request import base_campaign_request


class discount_campaign_request(base_campaign_request):
    campaign_type: str = "discount"
    discount_percentage: float
    product_id: Optional[UUID] = None
    min_total: Optional[float] = None