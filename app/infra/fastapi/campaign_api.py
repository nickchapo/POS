from datetime import datetime
from typing import List, Optional, Union
from pydantic import BaseModel, Field
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Path, Query

from ..core.domain.response.campaign_response import campaign_response
from ..core.domain.request.combo_campaign_request import combo_campaign_request
from ..core.domain.request.buy_N_get_N_campaign_request import buy_N_get_N_campaign_request
from ..core.domain.request.discount_campaign_request import discount_campaign_request
from ..core.campaign import Campaign, CampaignType, DiscountCampaign, BuyNGetNCampaign, ComboCampaign
from ..core.campaign_service import CampaignService
from ..dependencies import get_campaign_service

router = APIRouter(prefix="/campaigns", tags=["campaigns"])






CampaignRequest = Union[discount_campaign_request, buy_N_get_N_campaign_request, combo_campaign_request]




def request_to_campaign(req) -> Campaign:
    if req.campaign_type == "discount":
        return DiscountCampaign(
            active=req.active,
            start_date=req.start_date,
            end_date=req.end_date,
            discount_percentage=req.discount_percentage,
            product_id=req.product_id,
            min_total=req.min_total
        )
    elif req.campaign_type == "buy_n_get_n":
        return BuyNGetNCampaign(
            active=req.active,
            start_date=req.start_date,
            end_date=req.end_date,
            product_id=req.product_id,
            buy_quantity=req.buy_quantity,
            free_quantity=req.free_quantity
        )
    elif req.campaign_type == "combo":
        return ComboCampaign(
            active=req.active,
            start_date=req.start_date,
            end_date=req.end_date,
            combo_products=req.combo_products,
            combo_discount=req.combo_discount
        )
    raise ValueError(f"Unknown campaign type: {req.campaign_type}")


def campaign_to_response(campaign) -> campaign_response:
    response = campaign_response(
        id=campaign.id,
        campaign_type=campaign.campaign_type.value,
        active=campaign.active,
        start_date=campaign.start_date,
        end_date=campaign.end_date
    )

    if campaign.campaign_type == CampaignType.DISCOUNT:
        response.discount_percentage = campaign.discount_percentage
        response.product_id = campaign.product_id
        response.min_total = campaign.min_total
    elif campaign.campaign_type == CampaignType.BUY_N_GET_N:
        response.product_id = campaign.product_id
        response.buy_quantity = campaign.buy_quantity
        response.free_quantity = campaign.free_quantity
    elif campaign.campaign_type == CampaignType.COMBO:
        response.combo_products = campaign.combo_products
        response.combo_discount = campaign.combo_discount

    return response


@router.post("", response_model=campaign_response)
async def create_campaign(
        campaign_request: Union[discount_campaign_request, buy_N_get_N_campaign_request, combo_campaign_request],
        campaign_service: CampaignService = Depends(get_campaign_service)
):
    try:
        campaign = request_to_campaign(campaign_request)
        result = campaign_service.create_campaign(campaign)
        return campaign_to_response(result)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("", response_model=List[campaign_response])
async def list_campaigns(
        active_only: bool = Query(False, description="Filter for active campaigns only"),
        campaign_service: CampaignService = Depends(get_campaign_service)
):
    campaigns = campaign_service.list_campaigns(active_only=active_only)
    return [campaign_to_response(c) for c in campaigns]


@router.get("/{campaign_id}", response_model=campaign_response)
async def get_campaign(
        campaign_id: int = Path(..., description="The ID of the campaign to retrieve"),
        campaign_service: CampaignService = Depends(get_campaign_service)
):
    campaign = campaign_service.get_campaign(campaign_id)
    if not campaign:
        raise HTTPException(status_code=404, detail="Campaign not found")
    return campaign_to_response(campaign)


@router.delete("/{campaign_id}", status_code=204)
async def deactivate_campaign(
        campaign_id: int = Path(..., description="The ID of the campaign to deactivate"),
        campaign_service: CampaignService = Depends(get_campaign_service)
):
    success = campaign_service.deactivate_campaign(campaign_id)
    if not success:
        raise HTTPException(status_code=404, detail="Campaign not found")
    return None