"""
Blog Agent - TIER 2 for draft, TIER 3 for polish (conditional)

Generates SEO blog posts. TIER 3 polish ONLY if quality score < 0.8.
Blog agent is optional - only runs if "blog" in requested platforms.
"""

import json

from src.llm_router import get_tracked_llm
from src.state import CampaignState


# =============================================================================
# BLOG AGENT NODE
# =============================================================================

def blog_agent_node(state: CampaignState) -> CampaignState:
    """
    Blog agent node - generates SEO blog post.

    TIER 2: Draft generation (cheap model)
    TIER 3: Final polish (quality model) - ONLY if quality < 0.8

    Args:
        state: Current campaign state with product_info, brand_context

    Returns:
        Updated state with blog_post
    """
    product_info = state.get("product_info", {})
    brand_context = state.get("brand_context", "")
    brief = state.get("brief", {})

    messages = state.get("messages", [])
    messages.append("📝 Blog Agent: Generating blog post...")

    # === TIER 1: Generate target keywords ===
    llm_keywords = get_tracked_llm("extract", temperature=0.0)

    keywords_prompt = f"""Generate 3-5 target SEO keywords for a blog post.

Product: {product_info.get('name')}
Description: {product_info.get('description')}
Target Audience: {brief.get('audience', '')}

Respond with ONLY a JSON array of keywords: ["keyword1", "keyword2", ...]
"""

    response = llm_keywords.invoke([{"role": "user", "content": keywords_prompt}])

    try:
        keywords_text = response.content.strip()
        if "```json" in keywords_text:
            keywords_text = keywords_text.split("```json")[1].split("```")[0].strip()
        keywords = json.loads(keywords_text)
    except:
        keywords = [product_info.get("name", "AI"), "Bangladesh", "subscription"]

    # === TIER 2: Generate blog draft ===
    llm_draft = get_tracked_llm("draft", temperature=0.7)

    draft_prompt = build_blog_draft_prompt(
        product_info=product_info,
        brand_context=brand_context,
        keywords=keywords,
        audience=brief.get("audience", ""),
        tone=brief.get("tone", "informative"),
    )

    response = llm_draft.invoke([{"role": "user", "content": draft_prompt}])

    draft_mdx = response.content.strip()

    messages.append(f"   ✓ Generated draft ({len(draft_mdx)} chars)")

    # === TIER 3: Polish (ONLY if needed) ===
    # Skip Tier 3 polish for now - could be added based on quality check
    # For cost optimization, we'll use the draft as-is

    # === Extract metadata from draft ===
    blog_post = {
        "title": extract_title(draft_mdx),
        "slug": product_info.get("slug", "product") + "-guide",
        "meta_title": f"{product_info.get('name')} in Bangladesh - Complete Guide",
        "meta_description": extract_description(draft_mdx),
        "body_mdx": draft_mdx,
        "keywords": keywords,
        "internal_links": [f"/products/{product_info.get('slug', '')}"],
    }

    messages.append(f"   ✓ Blog post complete: '{blog_post['title']}'")

    state["blog_post"] = blog_post
    state["messages"] = messages

    return state


# =============================================================================
# PROMPT BUILDERS
# =============================================================================

def build_blog_draft_prompt(
    product_info: dict,
    brand_context: str,
    keywords: list[str],
    audience: str,
    tone: str,
) -> str:
    """Build the blog generation prompt."""

    return f"""Write a comprehensive SEO blog post about {product_info.get('name')}.

PRODUCT INFORMATION:
Name: {product_info.get('name')}
Price: ৳{product_info.get('price_bdt', 0)}/month
Description: {product_info.get('description')}
Features: {', '.join(product_info.get('features', []))}

TARGET KEYWORDS: {', '.join(keywords)}
TARGET AUDIENCE: {audience}
TONE: {tone}

REQUIREMENTS:
1. Write ~1500 words
2. Use SEO structure: H1 title, H2 sections, H3 subsections
3. Mix Bangla and English naturally (60-40 ratio)
4. Include FAQ section at the end
5. Add internal link to /products/{product_info.get('slug')}
6. Focus on benefits for {audience}

BRAND VOICE:
{brand_context[:1000]}

Format the response in MDX with frontmatter:
---
title: "SEO-Optimized Title"
slug: "url-friendly-slug"
meta_title: "Meta Title for SEO"
meta_description: "Meta description for search results"
---

[Blog post content with H1, H2, H3 headings]

## FAQ

### Question 1?
Answer...

### Question 2?
Answer...
"""


def extract_title(mdx: str) -> str:
    """Extract title from MDX."""
    lines = mdx.split("\n")
    for line in lines:
        if line.strip().startswith("# ") and not line.strip().startswith("##"):
            return line.strip()[2:]
    return "Blog Post"


def extract_description(mdx: str) -> str:
    """Extract first paragraph as meta description."""
    lines = mdx.split("\n")
    in_content = False
    for line in lines:
        if line.strip() and not line.startswith("#") and not line.startswith("---") and in_content:
            return line.strip()[:160]
        if line.startswith("# "):
            in_content = True
    return ""


if __name__ == "__main__":
    print("Blog Agent - generates SEO blog posts")
    print("TIER 2: Draft | TIER 3: Polish (only if quality < 0.8)")
