"""
Campaigns Schemas

Pydantic models for campaign operations.
"""

from pydantic import BaseModel, Field
from typing import Optional, List, Literal
from datetime import datetime


class CampaignBrief(BaseModel):
    """Campaign brief schema."""
    brand_id: str
    title: Optional[str] = None
    brief: str
    campaign_type: Optional[str] = None
    target_audience: Optional[str] = None
    tone: Optional[str] = None
    platforms: List[str]


class CampaignCreate(CampaignBrief):
    """Campaign creation schema."""
    pass


class ContentPieceDecision(BaseModel):
    """Human decision on a content piece."""
    action: Literal["approve", "reject"]
    feedback: Optional[str] = None


class CampaignReview(BaseModel):
    """Campaign review schema."""
    decisions: dict[str, ContentPieceDecision]


class CampaignResponse(BaseModel):
    """Campaign response schema."""
    id: str
    user_id: str
    brand_id: str
    title: Optional[str]
    brief: str
    campaign_type: Optional[str]
    target_audience: Optional[str]
    tone: Optional[str]
    platforms: List[str]
    status: str
    current_phase: str
    total_cost_usd: float
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class ContentPieceResponse(BaseModel):
    """Content piece response schema."""
    id: str
    campaign_id: str
    platform: str
    content_type: str
    copy: str
    hashtags: Optional[List[str]] = None
    image_urls: Optional[List[str]] = None
    cta_link: Optional[str] = None
    status: str
    feedback: Optional[str] = None
    llm_tier_used: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True
