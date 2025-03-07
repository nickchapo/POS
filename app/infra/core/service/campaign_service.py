from typing import List, Optional
from datetime import datetime
from uuid import UUID

from app.infra.core.campaign import Campaign, CampaignType, DiscountCampaign, BuyNGetNCampaign, ComboCampaign

class CampaignService:
    def __init__(self, repository):
        self.repository = repository

    def create_campaign(self, campaign: Campaign) -> Campaign:
        return self.repository.save(campaign)

    def get_campaign(self, campaign_id: int) -> Optional[Campaign]:
        return self.repository.find_by_id(campaign_id)

    def list_campaigns(self, active_only: bool = False) -> List[Campaign]:
        if active_only:
            return self.repository.find_active()
        return self.repository.find_all()

    def deactivate_campaign(self, campaign_id: int) -> bool:
        campaign = self.repository.find_by_id(campaign_id)
        if not campaign:
            return False
        campaign.active = False
        self.repository.save(campaign)
        return True

    def get_active_campaigns_for_product(self, product_id: UUID) -> List[Campaign]:
        return self.repository.find_active_for_product(product_id)

    def get_active_receipt_campaigns(self) -> List[Campaign]:
        return self.repository.find_active_receipt_campaigns()