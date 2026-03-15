"""
Test Copy Agent - Multi-Platform Copy Generation
"""

from src.agents.copy_agent import copy_agent_node


def test_copy_agent():
    """Test copy agent generates all platforms."""
    test_state = {
        "product_info": {
            "name": "ChatGPT Plus",
            "slug": "chatgpt-plus",
            "price_bdt": 2500,
            "description": "Premium GPT-4 access",
        },
        "brand_context": "Facebook: Bangla-heavy, emojis | Instagram: Aesthetic",
        "requested_platforms": ["facebook", "instagram"],
        "campaign_type": "deal_drop",
        "brief": {
            "audience": "Developers",
            "tone": "exciting",
        },
        "execution_plan": {"include_ad_variants": False},
        "messages": [],
        "content_pieces": [],
    }

    result = copy_agent_node(test_state)

    assert result.get("content_pieces") is not None
    assert len(result.get("content_pieces", [])) > 0
    print("✓ Copy agent generated content")

    for piece in result.get("content_pieces", []):
        assert piece["copy"] != ""
        assert piece["platform"] in ["facebook", "instagram"]
        print(f"  ✓ {piece['platform']}: {len(piece['copy'])} chars")


if __name__ == "__main__":
    print("Testing Copy Agent...")
    test_copy_agent()
    print("\n✓ All tests passed!")
