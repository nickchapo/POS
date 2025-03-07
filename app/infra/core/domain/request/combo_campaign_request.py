from typing import List
from uuid import UUID

import base_campaign_request

class combo_campaign_request(base_campaign_request):
    campaign_type: str = "combo"
    combo_products: List[UUID]
    combo_discount: float