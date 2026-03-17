"""
Campaigns Service

Business logic for campaign operations and LangGraph integration.
"""

import asyncio
import sys
from pathlib import Path
from typing import List, Optional

# Add src to path for agent imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent / "src"))

from src.state import initial_state, CampaignState
from src.graph.workflow import create_campaign_app
from src.llm_router import reset_cost_tracker, get_cost_tracker

from src.database import supabase
from src.campaigns.schemas import CampaignBrief, CampaignReview


class CampaignService:
    """Service for campaign operations."""

    @staticmethod
    def get_campaigns(user_id: str) -> List[dict]:
        """Get all campaigns for a user."""
        response = supabase.table('campaigns').select('*').eq('user_id', user_id).execute()
        return response.data

    @staticmethod
    def get_campaign(campaign_id: str, user_id: str) -> Optional[dict]:
        """Get a specific campaign by ID."""
        response = supabase.table('campaigns').select('*').eq('id', campaign_id).eq('user_id', user_id).single()
        return response.data

    @staticmethod
    def create_campaign(brief: CampaignBrief, user_id: str) -> dict:
        """Create a new campaign and trigger LangGraph workflow."""
        # Verify user owns the brand
        brand = supabase.table('brands').select('id').eq('id', brief.brand_id).eq('user_id', user_id).single()
        if not brand.data:
            raise ValueError("Brand not found or access denied")

        # Create campaign in database
        campaign_data = {
            "user_id": user_id,
            "brand_id": brief.brand_id,
            "title": brief.title,
            "brief": brief.brief,
            "campaign_type": brief.campaign_type,
            "target_audience": brief.target_audience,
            "tone": brief.tone,
            "platforms": brief.platforms,
            "status": "generating",
            "current_phase": "planning",
        }

        response = supabase.table('campaigns').insert(campaign_data).execute()
        campaign = response.data[0]

        # Trigger LangGraph workflow in background
        asyncio.create_task(CampaignService._run_langgraph_workflow(campaign['id'], brief.dict(), user_id))

        return campaign

    @staticmethod
    async def _run_langgraph_workflow(campaign_id: str, brief: dict, user_id: str):
        """Run LangGraph workflow in background task."""
        try:
            # Initialize cost tracker
            reset_cost_tracker()

            # Create initial state
            state = initial_state(brief)
            state["brief"]["campaign_id"] = campaign_id

            # Create and run app
            app = create_campaign_app()
            config = {"configurable": {"thread_id": campaign_id}}

            # Run workflow
            result = await app.ainvoke(state, config=config)

            # Get cost breakdown
            cost_tracker = get_cost_tracker()
            cost_summary = cost_tracker.get_summary()

            # Update campaign with results
            update_data = {
                "status": "review",
                "current_phase": "reviewing",
                "total_cost_usd": cost_summary.get("total_cost", 0),
                "cost_breakdown": cost_summary,
            }

            supabase.table('campaigns').update(update_data).eq('id', campaign_id).execute()

            # Insert content pieces
            content_pieces = result.get("content_pieces", [])
            for piece in content_pieces:
                piece_data = {
                    "campaign_id": campaign_id,
                    "platform": piece["platform"],
                    "content_type": piece["content_type"],
                    "copy": piece["copy"],
                    "hashtags": piece.get("hashtags"),
                    "cta_link": piece.get("cta_link"),
                    "metadata": piece.get("metadata", {}),
                    "llm_tier_used": piece.get("llm_tier_used"),
                    "status": "review",
                }
                supabase.table('content_pieces').insert(piece_data).execute()

        except Exception as e:
            # Update campaign status to failed
            supabase.table('campaigns').update({
                "status": "failed"
            }).eq('id', campaign_id).execute()
            raise e

    @staticmethod
    def get_content_pieces(campaign_id: str, user_id: str) -> List[dict]:
        """Get all content pieces for a campaign."""
        # Verify user owns the campaign
        campaign = supabase.table('campaigns').select('id').eq('id', campaign_id).eq('user_id', user_id).single()
        if not campaign.data:
            return []

        response = supabase.table('content_pieces').select('*').eq('campaign_id', campaign_id).execute()
        return response.data

    @staticmethod
    def review_campaign(campaign_id: str, review: CampaignReview, user_id: str) -> dict:
        """Submit human review and update content pieces."""
        # Verify user owns the campaign
        campaign = supabase.table('campaigns').select('id').eq('id', campaign_id).eq('user_id', user_id).single()
        if not campaign.data:
            raise ValueError("Campaign not found or access denied")

        # Update content pieces with decisions
        for piece_id, decision in review.decisions.items():
            update_data = {
                "status": "approved" if decision.action == "approve" else "rejected",
                "feedback": decision.feedback
            }
            supabase.table('content_pieces').update(update_data).eq('id', piece_id).eq('campaign_id', campaign_id).execute()

        # Update campaign status if all approved
        all_approved = all(d.action == "approve" for d in review.decisions.values())

        if all_approved:
            supabase.table('campaigns').update({
                "status": "approved"
            }).eq('id', campaign_id).execute()

        return {"message": "Review submitted successfully", "all_approved": all_approved}

    @staticmethod
    def get_campaign_cost(campaign_id: str, user_id: str) -> dict:
        """Get cost breakdown for a campaign."""
        campaign = CampaignService.get_campaign(campaign_id, user_id)
        if not campaign:
            raise ValueError("Campaign not found")

        return campaign.get("cost_breakdown", {})
