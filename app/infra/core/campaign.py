from datetime import datetime
from enum import Enum
from typing import List, Optional
from dataclasses import dataclass
from uuid import UUID


class CampaignType(Enum):
    DISCOUNT = "discount"
    BUY_N_GET_N = "buy_n_get_n"
    COMBO = "combo"


@dataclass
class Campaign:
    id: Optional[int] = None
    campaign_type: CampaignType = None
    active: bool = True
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None

    def is_valid_now(self) -> bool:
        now = datetime.now()
        if not self.active:
            return False
        if self.start_date and now < self.start_date:
            return False
        if self.end_date and now > self.end_date:
            return False
        return True


@dataclass
class DiscountCampaign(Campaign):
    discount_percentage: float = 0.0
    product_id: Optional[UUID] = None
    min_total: Optional[float] = None

    def __post_init__(self):
        self.campaign_type = CampaignType.DISCOUNT


@dataclass
class BuyNGetNCampaign(Campaign):
    product_id: Optional[UUID] = None
    buy_quantity: int = 0
    free_quantity: int = 0

    def __post_init__(self):
        self.campaign_type = CampaignType.BUY_N_GET_N


@dataclass
class ComboCampaign(Campaign):
    combo_products: List[UUID] = None
    combo_discount: float = 0.0

    def __post_init__(self):
        self.campaign_type = CampaignType.COMBO
        if self.combo_products is None:
            self.combo_products = []
