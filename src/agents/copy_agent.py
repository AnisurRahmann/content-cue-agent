"""
Copy Agent - TIER 2: Content Generation

Generates ALL platform copy in a SINGLE LLM call (major cost optimization).
This is the most important agent for cost efficiency.
"""

import json
from src.llm_router import get_tracked_llm
from src.state import CampaignState, create_content_piece


# =============================================================================
# COPY AGENT NODE
# =============================================================================

def copy_agent_node(state: CampaignState) -> CampaignState:
    """
    Copy agent node - generates all text content for all platforms.

    TIER 2: Content generation task (cheap model)
    CRITICAL: ALL platforms generated in ONE LLM call for cost optimization.

    Args:
        state: Current campaign state with product_info, brand_context

    Returns:
        Updated state with content_pieces (text only)
    """
    product_info = state.get("product_info", {})
    brand_context = state.get("brand_context", "")
    platforms = state.get("requested_platforms", [])
    campaign_type = state.get("campaign_type", "deal_drop")
    brief = state.get("brief", {})

    # Check if regenerating with feedback
    human_decisions = state.get("human_decisions", {})
    feedback_pieces = []
    if human_decisions:
        for piece_id, decision in human_decisions.items():
            if decision.get("action") == "reject":
                feedback_pieces.append({
                    "piece_id": piece_id,
                    "feedback": decision.get("feedback", ""),
                })

    messages = state.get("messages", [])

    if feedback_pieces:
        messages.append(f"✍️  Copy Agent: Regenerating {len(feedback_pieces)} pieces with feedback...")
    else:
        messages.append("✍️  Copy Agent: Generating all platform copy...")

    # === TIER 2: Generate ALL platform copy in ONE call ===
    # TIER 2: Content generation - use cheap model
    llm = get_tracked_llm("generate", temperature=0.7)

    # Build prompt with all platform guidelines
    prompt = build_copy_generation_prompt(
        product_info=product_info,
        brand_context=brand_context,
        platforms=platforms,
        campaign_type=campaign_type,
        audience=brief.get("audience", ""),
        tone=brief.get("tone", "casual"),
        instructions=brief.get("instructions", ""),
        include_ad_variants=state.get("execution_plan", {}).get("include_ad_variants", False),
        feedback_pieces=feedback_pieces,
    )

    response = llm.invoke([{"role": "user", "content": prompt}])

    # Parse JSON response
    try:
        response_text = response.content.strip()
        if "```json" in response_text:
            response_text = response_text.split("```json")[1].split("```")[0].strip()
        elif "```" in response_text:
            response_text = response_text.split("```")[1].split("```")[0].strip()

        generated_content = json.loads(response_text)
    except Exception as e:
        messages.append(f"   ⚠️ Failed to parse generated copy: {e}")
        generated_content = {}

    # === Create content pieces from generated content ===
    new_content_pieces = []

    # Platform-specific posts
    for platform in platforms:
        if platform not in generated_content:
            continue

        platform_content = generated_content[platform]

        # Skip if regenerating and this piece wasn't rejected
        if feedback_pieces:
            piece_id_to_regenerate = None
            for fp in feedback_pieces:
                if fp["piece_id"].startswith(platform):
                    piece_id_to_regenerate = fp["piece_id"]
                    break

            if not piece_id_to_regenerate:
                # Keep existing piece, don't regenerate
                existing_piece = next(
                    (p for p in state.get("content_pieces", []) if p["platform"] == platform and p["content_type"] == "post"),
                    None
                )
                if existing_piece:
                    new_content_pieces.append(existing_piece)
                    continue

        piece = create_content_piece(
            platform=platform,
            content_type="post",
            copy=platform_content.get("copy", ""),
            hashtags=platform_content.get("hashtags", []),
            llm_tier_used="tier_2",
        )
        new_content_pieces.append(piece)

    # Reel script (if generated)
    if "reel_script" in generated_content and generated_content["reel_script"]:
        reel = generated_content["reel_script"]
        reel_copy = f"""Hook: {reel.get('hook', '')}

Demo: {reel.get('body', '')}

CTA: {reel.get('cta', '')}"""

        piece = create_content_piece(
            platform="instagram",
            content_type="reel_script",
            copy=reel_copy,
            llm_tier_used="tier_2",
        )
        new_content_pieces.append(piece)

    # Ad variants (if requested)
    if "ad_variants" in generated_content:
        for i, variant in enumerate(generated_content["ad_variants"], 1):
            piece = create_content_piece(
                platform="facebook",
                content_type="ad",
                copy=variant.get("copy", ""),
                metadata={"angle": variant.get("angle", ""), "variant_number": i},
                llm_tier_used="tier_2",
            )
            new_content_pieces.append(piece)

    messages.append(f"   ✓ Generated {len(new_content_pieces)} content pieces")

    # === Update state ===
    # If regenerating, replace only the rejected pieces
    if feedback_pieces:
        existing_pieces = state.get("content_pieces", [])
        rejected_ids = {fp["piece_id"] for fp in feedback_pieces}

        # Keep non-rejected pieces
        kept_pieces = [p for p in existing_pieces if p["id"] not in rejected_ids]

        # Add newly generated pieces
        state["content_pieces"] = kept_pieces + new_content_pieces
    else:
        state["content_pieces"] = new_content_pieces

    state["messages"] = messages
    state["human_decisions"] = None  # Clear decisions after processing

    return state


# =============================================================================
# PROMPT BUILDER
# =============================================================================

def build_copy_generation_prompt(
    product_info: dict,
    brand_context: str,
    platforms: list[str],
    campaign_type: str,
    audience: str,
    tone: str,
    instructions: str,
    include_ad_variants: bool,
    feedback_pieces: list[dict] = None,
) -> str:
    """Build the comprehensive copy generation prompt."""

    product_name = product_info.get("name", "Product")
    product_desc = product_info.get("description", "")
    product_price = product_info.get("price_bdt", 0)
    product_features = product_info.get("features", [])

    prompt = f"""You are a copywriter for ContentCued, a Bangladeshi AI subscription service.

Generate marketing copy for the following product:

PRODUCT: {product_name}
PRICE: ৳{product_price}/month
DESCRIPTION: {product_desc}
FEATURES: {', '.join(product_features[:5])}

CAMPAIGN DETAILS:
- Campaign Type: {campaign_type}
- Target Audience: {audience}
- Tone: {tone}
- Special Instructions: {instructions}

BRAND GUIDELINES:
{brand_context[:2000]}  # Truncated for context

Generate copy for ALL requested platforms in a single JSON response:

{{
"""

    # Facebook
    if "facebook" in platforms:
        prompt += '''
    "facebook": {
        "copy": "<300 chars, Bangla-heavy, emojis, include price ৳{price}, WhatsApp CTA>",
        "hashtags": ["#ContentCued", "#AI", "#Bangladesh"]
    },
'''

    # Instagram
    if "instagram" in platforms:
        prompt += '''
    "instagram": {
        "copy": "<2200 chars, Bangla/English mix, 10-15 hashtags, aesthetic tone>",
        "hashtags": ["#ContentCued", "#AI", "#Bangladesh", "#Tech", ...]
    },
'''

    # LinkedIn
    if "linkedin" in platforms:
        prompt += '''
    "linkedin": {
        "copy": "<1300 chars, English-professional, value-driven, website CTA>"
    },
'''

    # WhatsApp
    if "whatsapp" in platforms:
        prompt += '''
    "whatsapp": {
        "copy": "<1000 chars, Bangla-brief, direct, bKash payment info, very short>"
    }
'''

    # Reel script (optional)
    if "instagram" in platforms:
        prompt += '''
    "reel_script": {
        "hook": "<3 second hook>",
        "body": "<15 second demo description>",
        "cta": "<5 second call to action>"
    },
'''

    # Ad variants (optional)
    if include_ad_variants:
        prompt += '''
    "ad_variants": [
        {"copy": "<price-focused ad copy>", "angle": "price"},
        {"copy": "<feature-focused ad copy>", "angle": "features"},
        {"copy": "<social proof ad copy>", "angle": "social_proof"}
    ]
'''

    # Feedback handling
    if feedback_pieces:
        prompt += f"""

FEEDBACK TO INCORPORATE:
{json.dumps(feedback_pieces, indent=2)}

Regenerate ONLY the rejected pieces with feedback incorporated.
"""

    prompt += """
}

CRITICAL RULES:
- ALL Facebook/Instagram posts MUST include WhatsApp CTA link
- NEVER mention G2A, reselling, keys, or cracks
- ALWAYS show price in BDT (৳)
- Use Bangla naturally mixed with English per platform
- Include emojis for Facebook/Instagram
- Respond with ONLY valid JSON, no markdown
"""

    return prompt


if __name__ == "__main__":
    # Test copy agent
    print("Testing Copy Agent\n")

    test_product = {
        "name": "ChatGPT Plus",
        "slug": "chatgpt-plus",
        "price_bdt": 2500,
        "description": "Premium access to GPT-4 for advanced AI conversations",
        "features": ["GPT-4 access", "Faster responses", "Early access to features"],
    }

    test_brand_context = """
    Facebook: Bangla-heavy, emojis, <300 chars, WhatsApp CTA
    Instagram: 50-50 Bangla/English, 10-15 hashtags, aesthetic
    """

    test_state = {
        "product_info": test_product,
        "brand_context": test_brand_context,
        "requested_platforms": ["facebook", "instagram"],
        "campaign_type": "deal_drop",
        "brief": {
            "audience": "Developers",
            "tone": "exciting",
            "instructions": "Focus on instant activation",
        },
        "execution_plan": {"include_ad_variants": True},
        "messages": [],
        "content_pieces": [],
    }

    result = copy_agent_node(test_state)

    print(f"Generated {len(result.get('content_pieces', []))} pieces:")
    for piece in result.get("content_pieces", [])[:3]:
        print(f"\n  {piece['platform']} ({piece['content_type']}):")
        print(f"  {piece['copy'][:100]}...")
