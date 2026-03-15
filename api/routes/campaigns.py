"""
Campaigns API Routes

Endpoints for creating, managing, and reviewing campaigns.
"""

from fastapi import APIRouter, HTTPException, BackgroundTasks
from pydantic import BaseModel
from typing import Optional, List

router = APIRouter()


# =============================================================================
# REQUEST/RESPONSE MODELS
# =============================================================================

class CampaignBrief(BaseModel):
    product_slug: str
    audience: str
    platforms: List[str]
    tone: str
    instructions: Optional[str] = ""


class CampaignCreate(BaseModel):
    brief: CampaignBrief


class HumanDecision(BaseModel):
    action: str  # "approve" or "reject"
    feedback: Optional[str] = ""


class CampaignReview(BaseModel):
    decisions: dict[str, HumanDecision]


# =============================================================================
# ENDPOINTS
# =============================================================================

@router.post("/campaigns")
async def create_campaign(request: CampaignCreate, background_tasks: BackgroundTasks):
    """Create a new campaign and trigger workflow."""
    import time

    campaign_id = f"campaign_{int(time.time())}"

    # Initialize state
    from src.state import initial_state
    from src.graph.workflow import create_campaign_app

    state = initial_state(request.brief.dict())
    state["brief"]["campaign_id"] = campaign_id

    # Run workflow in background (non-blocking)
    def run_workflow():
        app = create_campaign_app()
        config = {"configurable": {"thread_id": campaign_id}}
        app.invoke(state, config=config)

    background_tasks.add_task(run_workflow)

    return {
        "campaign_id": campaign_id,
        "status": "generating",
        "message": "Campaign generation started"
    }


@router.get("/campaigns")
async def list_campaigns():
    """List all campaigns."""
    from src.tools.file_tools import list_campaigns

    campaigns = list_campaigns()
    return {"campaigns": campaigns}


@router.get("/campaigns/{campaign_id}")
async def get_campaign(campaign_id: str):
    """Get full campaign details."""
    from src.tools.file_tools import load_campaign

    campaign = load_campaign(campaign_id)

    if not campaign:
        raise HTTPException(status_code=404, detail="Campaign not found")

    return campaign


@router.put("/campaigns/{campaign_id}/review")
async def review_campaign(campaign_id: str, review: CampaignReview):
    """Submit human review and resume workflow."""
    from src.tools.file_tools import load_campaign
    from src.graph.workflow import create_campaign_app

    # Load current campaign state
    campaign = load_campaign(campaign_id)

    if not campaign:
        raise HTTPException(status_code=404, detail="Campaign not found")

    # Update with human decisions
    campaign["human_decisions"] = review.decisions

    # Resume workflow
    app = create_campaign_app()
    config = {"configurable": {"thread_id": campaign_id}}

    result = app.invoke(campaign, config=config)

    return {
        "campaign_id": campaign_id,
        "status": result.get("current_phase"),
        "message": "Review processed"
    }


@router.get("/campaigns/{campaign_id}/cost")
async def get_campaign_cost(campaign_id: str):
    """Get cost breakdown for campaign."""
    from src.tools.file_tools import load_campaign

    campaign = load_campaign(campaign_id)

    if not campaign:
        raise HTTPException(status_code=404, detail="Campaign not found")

    cost_log = campaign.get("cost_log", [])

    # Calculate totals
    total_cost = sum(log.get("estimated_cost", 0) for log in cost_log)
    total_calls = len(cost_log)

    # Group by tier
    by_tier = {"tier_1": 0, "tier_2": 0, "tier_3": 0}
    for log in cost_log:
        tier = log.get("tier", "unknown")
        if tier in by_tier:
            by_tier[tier] += log.get("estimated_cost", 0)

    return {
        "campaign_id": campaign_id,
        "total_cost_usd": total_cost,
        "total_calls": total_calls,
        "by_tier": by_tier,
        "log": cost_log
    }


if __name__ == "__main__":
    print("Campaigns API Routes")
