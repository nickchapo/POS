from uuid import UUID

import base_campaign_request





class buy_N_get_N_campaign_request(base_campaign_request):
    campaign_type: str = "buy_n_get_n"
    product_id: UUID
    buy_quantity: int
    free_quantity: int

