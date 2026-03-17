"""
Campaign State

Placeholder for campaign state management.
TODO: Integrate with parent src/state.py
"""

from typing import TypedDict, Optional, List


class CampaignState(TypedDict):
    """State for campaign generation workflow."""
    brief: dict
    research: Optional[dict]
    content_pieces: List[dict]
    review: Optional[dict]
    final_status: str


def initial_state() -> CampaignState:
    """Create initial campaign state."""
    return {
        "brief": {},
        "research": None,
        "content_pieces": [],
        "review": None,
        "final_status": "initialized"
    }
