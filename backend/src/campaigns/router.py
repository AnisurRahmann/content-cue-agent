"""
Campaigns Router

Endpoints for campaign creation, listing, review, and cost tracking.
"""

from fastapi import APIRouter, HTTPException, Depends, BackgroundTasks
from typing import List

from backend.src.auth.dependencies import get_current_user_simple
from backend.src.campaigns.schemas import (
    CampaignCreate,
    CampaignResponse,
    CampaignReview,
    ContentPieceResponse
)
from backend.src.campaigns.service import CampaignService

router = APIRouter(prefix="/campaigns", tags=["campaigns"])


@router.get("", response_model=List[CampaignResponse])
async def get_campaigns(current_user: dict = Depends(get_current_user_simple)) -> List[dict]:
    """Get all campaigns for current user."""
    if not current_user:
        raise HTTPException(status_code=401, detail="Not authenticated")

    campaigns = CampaignService.get_campaigns(current_user['id'])
    return campaigns


@router.get("/{campaign_id}", response_model=CampaignResponse)
async def get_campaign(campaign_id: str, current_user: dict = Depends(get_current_user_simple)) -> dict:
    """Get a specific campaign."""
    if not current_user:
        raise HTTPException(status_code=401, detail="Not authenticated")

    campaign = CampaignService.get_campaign(campaign_id, current_user['id'])
    if not campaign:
        raise HTTPException(status_code=404, detail="Campaign not found")

    return campaign


@router.post("", response_model=CampaignResponse, status_code=201)
async def create_campaign(
    request: CampaignCreate,
    background_tasks: BackgroundTasks,
    current_user: dict = Depends(get_current_user_simple)
) -> dict:
    """Create a new campaign and trigger LangGraph workflow."""
    if not current_user:
        raise HTTPException(status_code=401, detail="Not authenticated")

    try:
        campaign = CampaignService.create_campaign(request, current_user['id'])
        return campaign
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to create campaign: {str(e)}")


@router.get("/{campaign_id}/content", response_model=List[ContentPieceResponse])
async def get_content_pieces(campaign_id: str, current_user: dict = Depends(get_current_user_simple)) -> List[dict]:
    """Get all content pieces for a campaign."""
    if not current_user:
        raise HTTPException(status_code=401, detail="Not authenticated")

    pieces = CampaignService.get_content_pieces(campaign_id, current_user['id'])
    return pieces


@router.put("/{campaign_id}/review")
async def review_campaign(
    campaign_id: str,
    review: CampaignReview,
    current_user: dict = Depends(get_current_user_simple)
) -> dict:
    """Submit human review for campaign content pieces."""
    if not current_user:
        raise HTTPException(status_code=401, detail="Not authenticated")

    try:
        result = CampaignService.review_campaign(campaign_id, review, current_user['id'])
        return result
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Review failed: {str(e)}")


@router.get("/{campaign_id}/cost")
async def get_campaign_cost(campaign_id: str, current_user: dict = Depends(get_current_user_simple)) -> dict:
    """Get cost breakdown for a campaign."""
    if not current_user:
        raise HTTPException(status_code=401, detail="Not authenticated")

    try:
        cost = CampaignService.get_campaign_cost(campaign_id, current_user['id'])
        return cost
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
