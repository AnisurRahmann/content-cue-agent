"""
Campaign State Schema

Defines the shared state that flows through the entire agent graph.
This is the single source of truth for campaign data.
"""

from typing import TypedDict, Optional, List, Literal, Annotated
import operator
from uuid import uuid4


class ContentPiece(TypedDict):
    """A single piece of content for one platform."""
    id: str                                    # Unique ID: "fb_post_001"
    platform: str                              # facebook | instagram | linkedin | whatsapp | blog
    content_type: str                          # post | carousel | reel_script | story | ad | broadcast
    copy: str                                  # The text content
    hashtags: Optional[List[str]]              # Platform-specific hashtags
    image_paths: Optional[List[str]]           # Generated image file paths
    image_prompts: Optional[List[str]]         # Prompts used for image gen
    cta_link: Optional[str]                    # WhatsApp deep link or website URL
    metadata: dict                             # aspect_ratio, char_count, word_count, etc.
    status: Literal["draft", "review", "approved", "rejected", "published"]
    feedback: Optional[str]                    # Human feedback if rejected
    llm_tier_used: str                         # Which tier generated this (for cost tracking)


class CampaignState(TypedDict):
    """The shared state that flows through the entire agent graph."""

    # === INPUT (from user) ===
    brief: dict                                # {product_slug, audience, platforms, tone, instructions}

    # === ORCHESTRATOR OUTPUT ===
    execution_plan: Optional[dict]             # Which agents to run, in what order
    requested_platforms: List[str]             # ["facebook", "instagram", "linkedin", "whatsapp"]
    campaign_type: Optional[str]               # deal_drop | education | social_proof | trending

    # === RAG CONTEXT (enriched by retriever) ===
    product_info: Optional[dict]               # Full product details from catalog
    brand_context: Optional[str]               # Relevant brand guidelines excerpt

    # === GENERATED CONTENT ===
    content_pieces: Annotated[list, operator.add]   # List[ContentPiece] — accumulates
    blog_post: Optional[dict]                  # {title, body_mdx, meta_title, meta_desc, faq}

    # === QUALITY & REVIEW ===
    quality_score: Optional[float]             # 0.0-1.0 from quality agent
    quality_issues: Optional[List[str]]        # List of problems found
    human_decisions: Optional[dict]            # {piece_id: "approved"|"rejected", feedback: "..."}

    # === SYSTEM ===
    current_phase: str                         # planning | generating | reviewing | publishing
    retry_count: int                           # How many quality-check retries
    cost_log: Annotated[list, operator.add]    # Token usage per LLM call
    messages: Annotated[list, operator.add]    # Step-by-step execution log
    errors: Annotated[list, operator.add]      # Error log


def create_content_piece(
    platform: str,
    content_type: str,
    copy: str,
    hashtags: Optional[List[str]] = None,
    image_paths: Optional[List[str]] = None,
    image_prompts: Optional[List[str]] = None,
    cta_link: Optional[str] = None,
    metadata: Optional[dict] = None,
    llm_tier_used: str = "unknown",
) -> ContentPiece:
    """Factory function to create a new ContentPiece with defaults."""
    return ContentPiece(
        id=f"{platform}_{content_type}_{str(uuid4())[:8]}",
        platform=platform,
        content_type=content_type,
        copy=copy,
        hashtags=hashtags or [],
        image_paths=image_paths or [],
        image_prompts=image_prompts or [],
        cta_link=cta_link,
        metadata=metadata or {},
        status="draft",
        feedback=None,
        llm_tier_used=llm_tier_used,
    )


def initial_state(brief: dict) -> CampaignState:
    """Create an initial campaign state from a brief."""
    return CampaignState(
        brief=brief,
        execution_plan=None,
        requested_platforms=brief.get("platforms", ["facebook", "instagram", "linkedin", "whatsapp"]),
        campaign_type=None,
        product_info=None,
        brand_context=None,
        content_pieces=[],
        blog_post=None,
        quality_score=None,
        quality_issues=None,
        human_decisions=None,
        current_phase="planning",
        retry_count=0,
        cost_log=[],
        messages=[],
        errors=[],
    )
