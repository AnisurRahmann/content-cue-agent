"""
Conditional Edge Routing Functions for LangGraph Workflow

These functions determine the flow of the campaign generation graph.
"""

from typing import Literal

from src.state import CampaignState


# =============================================================================
# ROUTING FUNCTIONS
# =============================================================================

def route_after_copy(state: CampaignState) -> Literal["blog_agent", "visual_agent"]:
    """
    Route after copy agent completes.

    - If blog requested → blog_agent
    - Otherwise → visual_agent
    """
    requested_platforms = state.get("requested_platforms", [])

    if "blog" in requested_platforms:
        return "blog_agent"

    return "visual_agent"


def route_after_quality(state: CampaignState) -> Literal["human_review", "orchestrator", "force_review"]:
    """
    Route after quality agent completes.

    - If quality_score >= 0.7 → human_review
    - If quality_score < 0.7 and retry_count < 2 → orchestrator (retry)
    - If retry_count >= 2 → force_review (show to human anyway)
    """
    quality_score = state.get("quality_score", 0.0)
    retry_count = state.get("retry_count", 0)

    if quality_score >= 0.7:
        return "human_review"

    if retry_count < 2:
        # Increment retry count
        state["retry_count"] = retry_count + 1
        state["messages"] = state.get("messages", []) + [
            f"⚠️ Quality score {quality_score:.2f} below threshold. Retrying..."
        ]
        return "orchestrator"

    # Max retries reached - force review anyway
    state["messages"] = state.get("messages", []) + [
        f"⚠️ Max retries reached. Quality score {quality_score:.2f}. Proceeding to review."
    ]
    return "force_review"


def route_after_review(state: CampaignState) -> Literal["save_campaign", "copy_agent"]:
    """
    Route after human review completes.

    - If all approved → save_campaign
    - If any rejected → copy_agent (regenerate with feedback)
    """
    human_decisions = state.get("human_decisions", {})

    if not human_decisions:
        # No decisions made - save as-is
        return "save_campaign"

    # Check if any rejections
    for piece_id, decision in human_decisions.items():
        if decision.get("action") == "reject":
            state["messages"] = state.get("messages", []) + [
                f"📝 Some content rejected. Regenerating with feedback..."
            ]
            return "copy_agent"

    # All approved
    return "save_campaign"


# =============================================================================
# HUMAN REVIEW NODE
# =============================================================================

def human_review_node(state: CampaignState) -> CampaignState:
    """
    Human review node - interrupts workflow for human approval.

    This is a pass-through node that marks state as ready for review.
    The actual interruption happens at the graph level.
    """
    messages = state.get("messages", [])
    messages.append("👤 Awaiting human review...")

    state["current_phase"] = "reviewing"
    state["messages"] = messages

    return state


# =============================================================================
# SAVE CAMPAIGN NODE
# =============================================================================

def save_campaign_node(state: CampaignState) -> CampaignState:
    """Save campaign node - persists all generated content."""
    from src.tools.file_tools import save_campaign, save_all_content_pieces
    from src.llm_router import get_cost_tracker, reset_cost_tracker

    import time
    campaign_id = f"campaign_{int(time.time())}"

    messages = state.get("messages", [])
    messages.append("💾 Saving campaign...")

    # Save campaign state
    campaign_file = save_campaign(state, campaign_id)
    messages.append(f"   ✓ Saved to: {campaign_file}")

    # Save content pieces
    content_files = save_all_content_pieces(state, campaign_id)
    messages.append(f"   ✓ Saved {len(content_files)} content pieces")

    # Print cost report
    messages.append("\n" + "=" * 50)
    messages.append("COST REPORT")
    messages.append("=" * 50)
    get_cost_tracker().print_report()
    messages.append("=" * 50 + "\n")

    # Reset for next campaign
    reset_cost_tracker()

    state["current_phase"] = "published"
    state["messages"] = messages

    return state


if __name__ == "__main__":
    print("Routing Functions - define conditional edges in LangGraph workflow")
