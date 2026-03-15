"""
Platform Adapter Agent - TIER 1: Formatting & Validation

Formats content for platform specifications, validates requirements,
adds metadata and CTAs. Mostly rule-based with minimal LLM usage.
"""

import os
from urllib.parse import urlencode

from src.llm_router import get_tracked_llm
from src.state import CampaignState


# =============================================================================
# ADAPTER AGENT NODE
# =============================================================================

def adapter_agent_node(state: CampaignState) -> CampaignState:
    """
    Adapter agent node - formats and validates all content pieces.

    TIER 1: Formatting/validation (minimal LLM, mostly rule-based)

    Args:
        state: Current campaign state with content_pieces

    Returns:
        Updated state with formatted content_pieces
    """
    content_pieces = state.get("content_pieces", [])
    product_info = state.get("product_info", {})

    messages = state.get("messages", [])
    messages.append("🔧 Adapter Agent: Formatting and validating content...")

    formatted_pieces = []
    issues_found = []

    for piece in content_pieces:
        # Format based on platform
        formatted, piece_issues = format_content_piece(piece, product_info)
        formatted_pieces.append(formatted)
        issues_found.extend(piece_issues)

    if issues_found:
        messages.append(f"   ⚠️ Found {len(issues_found)} formatting issues")
    else:
        messages.append(f"   ✓ Formatted {len(formatted_pieces)} pieces")

    state["content_pieces"] = formatted_pieces
    state["messages"] = messages

    return state


# =============================================================================
# FORMATTING FUNCTIONS
# =============================================================================

def format_content_piece(piece: dict, product_info: dict) -> tuple[dict, list[str]]:
    """Format a single content piece for its platform."""
    platform = piece["platform"]
    issues = []

    # Platform-specific formatting
    if platform == "facebook":
        piece, issues = format_facebook(piece, product_info)
    elif platform == "instagram":
        piece, issues = format_instagram(piece, product_info)
    elif platform == "linkedin":
        piece, issues = format_linkedin(piece, product_info)
    elif platform == "whatsapp":
        piece, issues = format_whatsapp(piece, product_info)

    # Common metadata
    copy = piece.get("copy", "")
    piece["metadata"]["char_count"] = len(copy)
    piece["metadata"]["word_count"] = len(copy.split())

    return piece, issues


def format_facebook(piece: dict, product_info: dict) -> tuple[dict, list[str]]:
    """Format Facebook post."""
    issues = []

    # Character limit: 300
    copy = piece.get("copy", "")
    if len(copy) > 300:
        copy = copy[:297] + "..."
        issues.append(f"{piece['id']}: Truncated to 300 chars")

    # Ensure WhatsApp CTA
    if "wa.me" not in copy.lower() and "whatsapp" not in copy.lower():
        whatsapp_number = os.getenv("WHATSAPP_NUMBER", "8801XXXXXXXXX")
        product_slug = product_info.get("slug", "")
        cta = f"\n\nWhatsApp: wa.me/{whatsapp_number}?text=I'm interested in {product_slug}"
        copy += cta

    # Hashtag count: 3-5
    hashtags = piece.get("hashtags", [])
    if len(hashtags) > 5:
        hashtags = hashtags[:5]
        issues.append(f"{piece['id']}: Hashtags reduced to 5")

    piece["copy"] = copy
    piece["hashtags"] = hashtags
    piece["cta_link"] = extract_whatsapp_link(copy)

    return piece, issues


def format_instagram(piece: dict, product_info: dict) -> tuple[dict, list[str]]:
    """Format Instagram post."""
    issues = []

    # Character limit: 2200
    copy = piece.get("copy", "")
    if len(copy) > 2200:
        copy = copy[:2197] + "..."
        issues.append(f"{piece['id']}: Truncated to 2200 chars")

    # Hashtag count: 10-15
    hashtags = piece.get("hashtags", [])
    if len(hashtags) < 10:
        # Add default hashtags
        hashtags.extend(["#ContentCued", "#AI", "#Bangladesh", "#Tech"])
    elif len(hashtags) > 15:
        hashtags = hashtags[:15]
        issues.append(f"{piece['id']}: Hashtags reduced to 15")

    piece["copy"] = copy
    piece["hashtags"] = list(set(hashtags))  # Dedupe
    piece["cta_link"] = extract_whatsapp_link(copy)

    return piece, issues


def format_linkedin(piece: dict, product_info: dict) -> tuple[dict, list[str]]:
    """Format LinkedIn post."""
    issues = []

    # Character limit: 1300
    copy = piece.get("copy", "")
    if len(copy) > 1300:
        # TIER 1: Intelligent truncation with LLM
        copy = intelligently_truncate(copy, 1300)
        issues.append(f"{piece['id']}: Truncated to 1300 chars")

    # Website CTA instead of WhatsApp
    if "contentcued.com" not in copy.lower():
        product_slug = product_info.get("slug", "")
        cta = f"\n\nLearn more: contentcued.com/{product_slug}"
        copy += cta

    # Hashtag count: 3-5
    hashtags = piece.get("hashtags", [])
    if len(hashtags) > 5:
        hashtags = hashtags[:5]
        issues.append(f"{piece['id']}: Hashtags reduced to 5")

    piece["copy"] = copy
    piece["hashtags"] = hashtags
    piece["cta_link"] = "https://contentcued.com/" + product_info.get("slug", "")

    return piece, issues


def format_whatsapp(piece: dict, product_info: dict) -> tuple[dict, list[str]]:
    """Format WhatsApp broadcast/status."""
    issues = []

    # Character limit: 1000 for broadcast
    copy = piece.get("copy", "")
    if len(copy) > 1000:
        copy = copy[:997] + "..."
        issues.append(f"{piece['id']}: Truncated to 1000 chars")

    # Add bKash payment info if not present
    if "bkash" not in copy.lower() and "বিকাশ" not in copy:
        copy += "\n\nবিকাশে পেমেন্ট করুন ✅"

    piece["copy"] = copy
    piece["hashtags"] = []  # No hashtags on WhatsApp

    return piece, issues


# =============================================================================
# UTILITY FUNCTIONS
# =============================================================================

def intelligently_truncate(text: str, max_length: int) -> str:
    """Truncate text intelligently at sentence boundary."""
    if len(text) <= max_length:
        return text

    # Try to truncate at sentence end
    truncated = text[:max_length]
    last_period = truncated.rfind(".")
    last_newline = truncated.rfind("\n")

    cutoff = max(last_period, last_newline)
    if cutoff > max_length * 0.8:  # Only if we're keeping at least 80%
        return text[:cutoff + 1].strip() + "..."

    return truncated + "..."


def extract_whatsapp_link(text: str) -> str | None:
    """Extract WhatsApp deep link from text."""
    import re

    match = re.search(r"wa\.me/[\d\?]+", text)
    if match:
        return "https://" + match.group(0)
    return None


if __name__ == "__main__":
    print("Platform Adapter Agent - formats and validates content")
    print("TIER 1: Mostly rule-based, minimal LLM usage")
