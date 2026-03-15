"""
Visual Agent - TIER 1 for prompts, Ideogram API for images

Generates image prompts (TIER 1) and creates images via Ideogram API.
"""

import asyncio
from pathlib import Path

from src.llm_router import get_tracked_llm
from src.tools.ideogram_tool import generate_image
from src.tools.image_resizer import resize_image, PlatformSpec
from src.state import CampaignState


# =============================================================================
# VISUAL AGENT NODE
# =============================================================================

def visual_agent_node(state: CampaignState) -> CampaignState:
    """
    Visual agent node - generates images for all visual content pieces.

    TIER 1: Image prompt generation (free model)
    External API: Actual image generation (Ideogram or placeholder)

    Args:
        state: Current campaign state with content_pieces

    Returns:
        Updated state with content_pieces having image_paths
    """
    content_pieces = state.get("content_pieces", [])
    product_info = state.get("product_info", {})
    campaign_id = state.get("brief", {}).get("campaign_id", "temp_campaign")

    messages = state.get("messages", [])
    messages.append("🎨 Visual Agent: Generating images...")

    # Get pieces that need images
    visual_platforms = ["facebook", "instagram", "linkedin", "whatsapp"]
    pieces_needing_images = [
        p for p in content_pieces
        if p["platform"] in visual_platforms
        and p["content_type"] in ("post", "ad", "carousel")
        and not p.get("image_paths")  # Don't regenerate if already has images
    ]

    if not pieces_needing_images:
        messages.append("   ℹ️  No pieces need images")
        state["messages"] = messages
        return state

    # Generate images for each piece
    updated_pieces = []
    for piece in content_pieces:
        if piece in pieces_needing_images:
            # Generate image
            image_path = generate_image_for_piece(piece, product_info, campaign_id)
            piece["image_paths"] = [image_path] if image_path else []
            piece["image_prompts"] = [piece.get("image_prompt", "")]

        updated_pieces.append(piece)

    messages.append(f"   ✓ Generated images for {len(pieces_needing_images)} pieces")

    state["content_pieces"] = updated_pieces
    state["messages"] = messages

    return state


# =============================================================================
# IMAGE GENERATION
# =============================================================================

def generate_image_for_piece(piece: dict, product_info: dict, campaign_id: str) -> str:
    """Generate an image for a content piece."""

    # === TIER 1: Generate image prompt ===
    # TIER 1: Prompt engineering - use free model
    llm = get_tracked_llm("format", temperature=0.0)

    product_name = product_info.get("name", "Product")
    product_price = product_info.get("price_bdt", 0)
    copy_text = piece.get("copy", "")[:200]

    prompt_request = f"""Create a detailed image generation prompt for a marketing image.

Product: {product_name}
Price: ৳{product_price}/month
Copy: {copy_text}

Create a prompt for:
- Platform: {piece['platform']}
- Style: Modern tech, clean, dark gradient background (#1A365D to #0F172A)
- Colors: Blue (#3B82F6) and purple (#8B5CF6) accents
- Text overlay: Key message from the copy
- Aspect ratio: {get_aspect_ratio_for_platform(piece['platform'])}

Respond with ONLY the image prompt, no explanation.
"""

    response = llm.invoke([{"role": "user", "content": prompt_request}])
    image_prompt = response.content.strip()

    # Store prompt
    piece["image_prompt"] = image_prompt

    # === Generate image ===
    output_dir = Path("outputs") / campaign_id / "images"
    output_dir.mkdir(parents=True, exist_ok=True)

    output_path = str(output_dir / f"{piece['id']}.png")

    # Run async generation
    image_path, is_real = asyncio.run(generate_image(
        prompt=image_prompt,
        output_path=output_path,
        aspect_ratio=get_aspect_ratio_for_platform(piece["platform"]),
    ))

    if not is_real:
        # If placeholder, still store the path
        return image_path

    # Resize to platform spec
    platform_spec = get_platform_spec(piece["platform"])
    if platform_spec:
        resized_path = output_path.replace(".png", f"_{platform_spec}.jpg")
        try:
            image_path = resize_image(image_path, resized_path, platform_spec)
        except Exception as e:
            print(f"⚠️ Failed to resize {piece['id']}: {e}")

    return image_path


def get_aspect_ratio_for_platform(platform: str) -> str:
    """Get Ideogram aspect ratio for platform."""
    ratios = {
        "facebook": "16:9",
        "instagram": "1:1",
        "linkedin": "16:9",
        "whatsapp": "9:16",
    }
    return ratios.get(platform, "1:1")


def get_platform_spec(platform: str) -> str | None:
    """Get image resizer platform spec."""
    specs = {
        "facebook": "facebook_post",
        "instagram": "instagram_square",
        "linkedin": "linkedin_post",
        "whatsapp": "whatsapp_status",
    }
    return specs.get(platform)


if __name__ == "__main__":
    print("Visual Agent - generates images for content pieces")
    print("TIER 1: Prompt generation | External: Ideogram API")
