"""
Orchestrator Agent - TIER 1: Planning & Routing

Parses campaign brief, retrieves RAG context, and builds execution plan.
This is the entry point for all campaigns.
"""

import json
from typing import Literal

from src.llm_router import get_tracked_llm
from src.state import CampaignState
from src.rag.retriever import get_context_for_campaign


# =============================================================================
# ORCHESTRATOR NODE
# =============================================================================

def orchestrator_node(state: CampaignState) -> CampaignState:
    """
    Orchestrator agent node - first node in the workflow.

    TIER 1: Routing/classification task (free/cheap)

    Steps:
    1. Parse brief into structured fields
    2. Classify campaign type
    3. Retrieve product info via RAG
    4. Retrieve brand context via RAG
    5. Build execution plan

    Args:
        state: Current campaign state with brief

    Returns:
        Updated state with execution_plan, product_info, brand_context
    """
    brief = state.get("brief", {})

    # Extract basic fields from brief
    product_slug = brief.get("product_slug")
    audience = brief.get("audience", "General")
    platforms = brief.get("platforms", ["facebook", "instagram", "linkedin", "whatsapp"])
    tone = brief.get("tone", "casual")
    instructions = brief.get("instructions", "")

    messages = state.get("messages", [])
    messages.append("🎯 Orchestrator: Parsing brief and building execution plan...")

    # === TIER 1: Classify campaign type ===
    # TIER 1: Classification task - use free/cheap model
    llm_classify = get_tracked_llm("classify", temperature=0.0)

    classify_prompt = f"""Classify this campaign brief into ONE of these types:

Campaign Types:
- deal_drop: Promotional content highlighting discounts/offers
- education: How-to guides, tutorials, tips
- social_proof: Customer testimonials, reviews, case studies
- trending: Industry news, trending topics, new features

Brief:
- Product: {product_slug}
- Audience: {audience}
- Tone: {tone}
- Instructions: {instructions}

Respond with ONLY the campaign type (e.g., "deal_drop").
"""

    response = llm_classify.invoke([{"role": "user", "content": classify_prompt}])
    campaign_type = response.content.strip().lower()

    # Normalize campaign type
    valid_types = ["deal_drop", "education", "social_proof", "trending"]
    if campaign_type not in valid_types:
        campaign_type = "deal_drop"  # Default

    messages.append(f"   ✓ Classified as: {campaign_type}")

    # === Retrieve RAG context ===
    product_info, brand_context = get_context_for_campaign(
        product_slug=product_slug,
        brand_query="platform-specific tone and formatting guidelines"
    )

    if not product_info:
        messages.append(f"   ⚠️ Product '{product_slug}' not found in catalog")
        # Create minimal product info from brief
        product_info = {
            "slug": product_slug,
            "name": product_slug.replace("-", " ").title(),
            "price_bdt": 0,
            "category": "Unknown",
        }
    else:
        messages.append(f"   ✓ Found product: {product_info.get('name')}")

    if brand_context:
        messages.append(f"   ✓ Retrieved brand context ({len(brand_context)} chars)")

    # === TIER 1: Build execution plan ===
    llm_plan = get_tracked_llm("route", temperature=0.0)

    include_blog = "blog" in platforms
    include_ad_variants = campaign_type == "deal_drop"

    plan_prompt = f"""Build an execution plan for this marketing campaign.

Campaign Details:
- Product: {product_info.get('name')} (৳{product_info.get('price_bdt', 0)}/month)
- Campaign Type: {campaign_type}
- Platforms: {', '.join(platforms)}
- Audience: {audience}
- Include Blog: {include_blog}
- Include Ad Variants: {include_ad_variants}

Respond with a JSON object:
{{
    "agents_to_run": ["copy_agent", "visual_agent", {"blog_agent" if include_blog else ""}],
    "parallel": true,
    "platforms": {platforms},
    "include_blog": {str(include_blog).lower()},
    "include_ad_variants": {str(include_ad_variants).lower()},
    "content_pieces_count_estimate": <estimated number of content pieces>
}}

Remove the blog_agent from agents_to_run if include_blog is false.
Respond ONLY with valid JSON.
"""

    response = llm_plan.invoke([{"role": "user", "content": plan_prompt}])

    try:
        # Parse JSON from response
        plan_text = response.content.strip()
        if "```json" in plan_text:
            plan_text = plan_text.split("```json")[1].split("```")[0].strip()
        elif "```" in plan_text:
            plan_text = plan_text.split("```")[1].split("```")[0].strip()

        execution_plan = json.loads(plan_text)
    except Exception as e:
        messages.append(f"   ⚠️ Failed to parse execution plan: {e}")
        # Fallback plan
        execution_plan = {
            "agents_to_run": ["copy_agent", "visual_agent"],
            "parallel": True,
            "platforms": platforms,
            "include_blog": include_blog,
            "include_ad_variants": include_ad_variants,
            "content_pieces_count_estimate": len(platforms) + (3 if include_ad_variants else 0),
        }

    messages.append(f"   ✓ Execution plan: {execution_plan.get('agents_to_run')}")

    # === Update state ===
    state["execution_plan"] = execution_plan
    state["requested_platforms"] = platforms
    state["campaign_type"] = campaign_type
    state["product_info"] = product_info
    state["brand_context"] = brand_context
    state["current_phase"] = "generating"
    state["messages"] = messages

    return state


if __name__ == "__main__":
    # Test orchestrator
    print("Testing Orchestrator Agent\n")

    test_brief = {
        "product_slug": "chatgpt-plus",
        "audience": "Developers and content creators",
        "platforms": ["facebook", "instagram", "linkedin", "whatsapp"],
        "tone": "exciting",
        "instructions": "Focus on the instant activation benefit and local pricing",
    }

    test_state = {
        "brief": test_brief,
        "messages": [],
    }

    result = orchestrator_node(test_state)

    print("Execution Plan:")
    print(f"  Campaign Type: {result.get('campaign_type')}")
    print(f"  Platforms: {result.get('requested_platforms')}")
    print(f"  Product: {result.get('product_info', {}).get('name')}")
    print(f"  Agents: {result.get('execution_plan', {}).get('agents_to_run')}")
    print(f"\nMessages:")
    for msg in result.get("messages", []):
        print(f"  {msg}")
