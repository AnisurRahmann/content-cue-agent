"""
File Tools - Save and load campaign assets.

Handles:
- Saving generated content pieces
- Saving blog posts
- Loading campaign data
- Exporting campaigns as JSON
"""

import json
import os
from pathlib import Path
from datetime import datetime
from typing import Optional

from src.state import CampaignState, ContentPiece


# =============================================================================
# CONFIGURATION
# =============================================================================

OUTPUTS_DIR = os.getenv("CAMPAIGN_OUTPUTS_DIR", "./outputs")


def get_campaign_dir(campaign_id: str) -> Path:
    """Get the directory path for a campaign."""
    return Path(OUTPUTS_DIR) / campaign_id


def ensure_campaign_dir(campaign_id: str) -> Path:
    """Create campaign directory if it doesn't exist."""
    campaign_dir = get_campaign_dir(campaign_id)
    campaign_dir.mkdir(parents=True, exist_ok=True)
    return campaign_dir


# =============================================================================
# SAVE CAMPAIGN
# =============================================================================

def save_campaign(state: CampaignState, campaign_id: str) -> str:
    """
    Save complete campaign state to JSON file.

    Args:
        state: CampaignState to save
        campaign_id: Unique campaign identifier

    Returns:
        Path to saved campaign file
    """
    campaign_dir = ensure_campaign_dir(campaign_id)
    campaign_file = campaign_dir / "campaign.json"

    # Convert state to JSON-serializable dict
    campaign_data = {
        "campaign_id": campaign_id,
        "saved_at": datetime.now().isoformat(),
        "brief": state.get("brief"),
        "execution_plan": state.get("execution_plan"),
        "requested_platforms": state.get("requested_platforms"),
        "campaign_type": state.get("campaign_type"),
        "product_info": state.get("product_info"),
        "brand_context": state.get("brand_context"),
        "content_pieces": state.get("content_pieces", []),
        "blog_post": state.get("blog_post"),
        "quality_score": state.get("quality_score"),
        "quality_issues": state.get("quality_issues"),
        "human_decisions": state.get("human_decisions"),
        "current_phase": state.get("current_phase"),
        "retry_count": state.get("retry_count"),
        "cost_log": state.get("cost_log", []),
        "messages": state.get("messages", []),
        "errors": state.get("errors", []),
    }

    # Write to file
    with open(campaign_file, "w", encoding="utf-8") as f:
        json.dump(campaign_data, f, indent=2, ensure_ascii=False)

    return str(campaign_file)


def load_campaign(campaign_id: str) -> Optional[dict]:
    """
    Load campaign state from JSON file.

    Args:
        campaign_id: Campaign identifier

    Returns:
        Campaign data dict or None if not found
    """
    campaign_file = get_campaign_dir(campaign_id) / "campaign.json"

    if not campaign_file.exists():
        return None

    with open(campaign_file, "r", encoding="utf-8") as f:
        return json.load(f)


# =============================================================================
# SAVE CONTENT PIECES
# =============================================================================

def save_content_piece(piece: ContentPiece, campaign_id: str) -> str:
    """
    Save a content piece to individual JSON file.

    Args:
        piece: ContentPiece to save
        campaign_id: Campaign identifier

    Returns:
        Path to saved content piece file
    """
    campaign_dir = ensure_campaign_dir(campaign_id)

    # Create content subdirectory
    content_dir = campaign_dir / "content"
    content_dir.mkdir(exist_ok=True)

    # Save to file
    filename = f"{piece['id']}.json"
    content_file = content_dir / filename

    with open(content_file, "w", encoding="utf-8") as f:
        json.dump(piece, f, indent=2, ensure_ascii=False)

    return str(content_file)


def save_all_content_pieces(state: CampaignState, campaign_id: str) -> list[str]:
    """
    Save all content pieces from campaign state.

    Args:
        state: CampaignState with content_pieces
        campaign_id: Campaign identifier

    Returns:
        List of saved file paths
    """
    saved_paths = []

    for piece in state.get("content_pieces", []):
        path = save_content_piece(piece, campaign_id)
        saved_paths.append(path)

    return saved_paths


# =============================================================================
# SAVE BLOG POST
# =============================================================================

def save_blog_post(blog_post: dict, campaign_id: str) -> tuple[str, str]:
    """
    Save blog post as both JSON and MDX.

    Args:
        blog_post: Blog post dict with title, body_mdx, etc.
        campaign_id: Campaign identifier

    Returns:
        Tuple of (json_path, mdx_path)
    """
    campaign_dir = ensure_campaign_dir(campaign_id)

    # Save JSON
    blog_json = campaign_dir / "blog_post.json"
    with open(blog_json, "w", encoding="utf-8") as f:
        json.dump(blog_post, f, indent=2, ensure_ascii=False)

    # Save MDX
    slug = blog_post.get("slug", "post")
    blog_mdx = campaign_dir / f"{slug}.mdx"

    # Create MDX content with frontmatter
    frontmatter = {
        "title": blog_post.get("title"),
        "slug": blog_post.get("slug"),
        "meta_title": blog_post.get("meta_title"),
        "meta_description": blog_post.get("meta_description"),
        "keywords": blog_post.get("keywords", []),
    }

    mdx_content = "---\n"
    for key, value in frontmatter.items():
        if isinstance(value, list):
            mdx_content += f"{key}: {json.dumps(value)}\n"
        else:
            mdx_content += f"{key}: {json.dumps(value)}\n"
    mdx_content += "---\n\n"
    mdx_content += blog_post.get("body_mdx", "")

    with open(blog_mdx, "w", encoding="utf-8") as f:
        f.write(mdx_content)

    return str(blog_json), str(blog_mdx)


# =============================================================================
# EXPORT CAMPAIGN
# =============================================================================

def export_campaign_text(campaign_id: str, output_path: Optional[str] = None) -> str:
    """
    Export campaign as human-readable text file.

    Args:
        campaign_id: Campaign identifier
        output_path: Optional output path (default: campaign_dir/export.txt)

    Returns:
        Path to exported text file
    """
    # Load campaign
    campaign_data = load_campaign(campaign_id)
    if not campaign_data:
        raise FileNotFoundError(f"Campaign {campaign_id} not found")

    # Default output path
    if output_path is None:
        campaign_dir = get_campaign_dir(campaign_id)
        output_path = campaign_dir / "export.txt"

    # Build text export
    lines = []
    lines.append("=" * 60)
    lines.append(f"CONTENTCUED CAMPAIGN EXPORT")
    lines.append(f"Campaign ID: {campaign_id}")
    lines.append(f"Saved: {campaign_data.get('saved_at', 'Unknown')}")
    lines.append("=" * 60)
    lines.append("")

    # Brief
    lines.append("## BRIEF")
    brief = campaign_data.get("brief", {})
    lines.append(f"Product: {brief.get('product_slug', 'Unknown')}")
    lines.append(f"Audience: {brief.get('audience', 'Unknown')}")
    lines.append(f"Platforms: {', '.join(brief.get('platforms', []))}")
    lines.append("")

    # Content Pieces
    lines.append("## CONTENT PIECES")
    for piece in campaign_data.get("content_pieces", []):
        lines.append(f"\n### {piece['id']}")
        lines.append(f"Platform: {piece['platform']}")
        lines.append(f"Type: {piece['content_type']}")
        lines.append(f"Status: {piece['status']}")
        lines.append(f"\nCopy:\n{piece['copy']}")
        if piece.get("hashtags"):
            lines.append(f"\nHashtags: {', '.join(piece['hashtags'])}")
        if piece.get("cta_link"):
            lines.append(f"CTA: {piece['cta_link']}")
        lines.append("")

    # Blog Post
    if campaign_data.get("blog_post"):
        lines.append("## BLOG POST")
        blog = campaign_data["blog_post"]
        lines.append(f"Title: {blog.get('title')}")
        lines.append(f"\n{blog.get('body_mdx', '')[:500]}...")
        lines.append("")

    # Quality Score
    if campaign_data.get("quality_score"):
        lines.append(f"## QUALITY SCORE: {campaign_data['quality_score']:.2f}")
        if campaign_data.get("quality_issues"):
            lines.append(f"Issues: {', '.join(campaign_data['quality_issues'])}")
        lines.append("")

    # Write to file
    with open(output_path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))

    return str(output_path)


# =============================================================================
# LIST CAMPAIGNS
# =============================================================================

def list_campaigns() -> list[dict]:
    """
    List all campaigns with basic metadata.

    Returns:
        List of campaign info dicts
    """
    outputs_path = Path(OUTPUTS_DIR)

    if not outputs_path.exists():
        return []

    campaigns = []

    for campaign_dir in outputs_path.iterdir():
        if not campaign_dir.is_dir():
            continue

        campaign_file = campaign_dir / "campaign.json"
        if not campaign_file.exists():
            continue

        try:
            with open(campaign_file, "r", encoding="utf-8") as f:
                data = json.load(f)

            campaigns.append({
                "campaign_id": campaign_dir.name,
                "product": data.get("brief", {}).get("product_slug"),
                "saved_at": data.get("saved_at"),
                "platforms": data.get("requested_platforms", []),
                "content_count": len(data.get("content_pieces", [])),
            })
        except Exception as e:
            print(f"⚠️ Failed to load campaign {campaign_dir.name}: {e}")

    # Sort by saved_at (newest first)
    campaigns.sort(key=lambda x: x.get("saved_at", ""), reverse=True)

    return campaigns


if __name__ == "__main__":
    # Test file tools
    print("File Tools Test\n")

    # Create a test campaign
    test_state = {
        "brief": {
            "product_slug": "chatgpt-plus",
            "audience": "Developers",
            "platforms": ["facebook", "instagram"],
        },
        "content_pieces": [
            {
                "id": "fb_test_001",
                "platform": "facebook",
                "content_type": "post",
                "copy": "Test post",
                "status": "draft",
            }
        ],
        "quality_score": 0.85,
    }

    # Save campaign
    campaign_id = "test_campaign_001"
    path = save_campaign(test_state, campaign_id)
    print(f"✅ Saved campaign to: {path}")

    # List campaigns
    campaigns = list_campaigns()
    print(f"\n📊 Found {len(campaigns)} campaign(s)")
    for c in campaigns:
        print(f"   - {c['campaign_id']}: {c.get('product', 'Unknown')}")
