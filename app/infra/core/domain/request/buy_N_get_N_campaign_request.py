from uuid import UUID

import base_campaign_request





class BuyNGetNCampaignRequest(base_campaign_request):
    campaign_type: str = "buy_n_get_n"
    product_id: UUID
    buy_quantity: int
    free_quantity: int

