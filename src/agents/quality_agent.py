"""
Quality Agent - TIER 1: Validation & Brand Compliance

Validates all content pieces against brand guidelines and requirements.
Mix of rule-based checks (zero cost) and TIER 1 LLM validation.
"""

from src.llm_router import get_tracked_llm
from src.state import CampaignState


# =============================================================================
# QUALITY AGENT NODE
# =============================================================================

def quality_agent_node(state: CampaignState) -> CampaignState:
    """
    Quality agent node - validates content and calculates quality score.

    TIER 1: Validation checks (free model for LLM checks)
    Mix of rule-based (zero cost) and LLM-based validation

    Args:
        state: Current campaign state with content_pieces

    Returns:
        Updated state with quality_score and quality_issues
    """
    content_pieces = state.get("content_pieces", [])
    product_info = state.get("product_info", {})
    brand_context = state.get("brand_context", "")

    messages = state.get("messages", [])
    messages.append("✓ Quality Agent: Validating content...")

    # Run rule-based checks (zero cost)
    rule_based_results = run_rule_based_checks(content_pieces, product_info)

    # Run LLM-based checks (TIER 1)
    llm_based_results = run_llm_based_checks(content_pieces, brand_context)

    # Calculate quality score
    quality_score, quality_issues = calculate_quality_score(
        rule_based_results,
        llm_based_results
    )

    messages.append(f"   Quality Score: {quality_score:.2f}")

    if quality_issues:
        messages.append(f"   Issues: {', '.join(quality_issues[:3])}")
        if len(quality_issues) > 3:
            messages.append(f"   ... and {len(quality_issues) - 3} more")

    # Update state
    state["quality_score"] = quality_score
    state["quality_issues"] = quality_issues
    state["messages"] = messages

    # Update piece statuses
    updated_pieces = []
    for piece in content_pieces:
        piece["status"] = "review"  # Ready for human review
        updated_pieces.append(piece)

    state["content_pieces"] = updated_pieces

    return state


# =============================================================================
# RULE-BASED CHECKS (ZERO LLM COST)
# =============================================================================

def run_rule_based_checks(content_pieces: list[dict], product_info: dict) -> dict:
    """Run rule-based validation checks (zero cost)."""
    results = {
        "passed_checks": [],
        "failed_checks": [],
    }

    product_price = product_info.get("price_bdt", 0)

    for piece in content_pieces:
        platform = piece["platform"]
        copy = piece.get("copy", "")
        hashtags = piece.get("hashtags", [])

        # Check 1: BDT price appears in Facebook/Instagram copy
        if platform in ("facebook", "instagram"):
            if "৳" not in copy and str(product_price) not in copy:
                results["failed_checks"].append(f"{piece['id']}: Missing BDT price")
            else:
                results["passed_checks"].append(f"{piece['id']}: Has BDT price")

        # Check 2: WhatsApp CTA link present in Facebook/Instagram content
        if platform in ("facebook", "instagram"):
            if "wa.me" not in copy.lower() and "whatsapp" not in copy.lower():
                results["failed_checks"].append(f"{piece['id']}: Missing WhatsApp CTA")
            else:
                results["passed_checks"].append(f"{piece['id']}: Has WhatsApp CTA")

        # Check 3: No mention of G2A/reselling (brand safety)
        forbidden_terms = ["g2a", "reseller", "reselling", "key", "crack"]
        found_forbidden = [term for term in forbidden_terms if term.lower() in copy.lower()]
        if found_forbidden:
            results["failed_checks"].append(f"{piece['id']}: Forbidden terms: {', '.join(found_forbidden)}")
        else:
            results["passed_checks"].append(f"{piece['id']}: No forbidden terms")

        # Check 4: Character limits respected
        char_limits = {
            "facebook": 300,
            "instagram": 2200,
            "linkedin": 1300,
            "whatsapp": 1000,
        }
        if platform in char_limits:
            if len(copy) > char_limits[platform]:
                results["failed_checks"].append(f"{piece['id']}: Exceeds {char_limits[platform]} char limit")
            else:
                results["passed_checks"].append(f"{piece['id']}: Within char limit")

        # Check 5: Hashtag count appropriate
        if platform == "instagram":
            if not (10 <= len(hashtags) <= 15):
                results["failed_checks"].append(f"{piece['id']}: Instagram needs 10-15 hashtags (has {len(hashtags)})")
            else:
                results["passed_checks"].append(f"{piece['id']}: Hashtag count OK")
        elif platform in ("facebook", "linkedin"):
            if len(hashtags) > 5:
                results["failed_checks"].append(f"{piece['id']}: {platform} needs max 5 hashtags (has {len(hashtags)})")
            else:
                results["passed_checks"].append(f"{piece['id']}: Hashtag count OK")

        # Check 6: Images generated for visual platforms
        if platform in ("facebook", "instagram", "linkedin"):
            if not piece.get("image_paths"):
                results["failed_checks"].append(f"{piece['id']}: Missing image")
            else:
                results["passed_checks"].append(f"{piece['id']}: Has image")

    # Check 7: At least 3 ad variants generated (if applicable)
    ad_variants = [p for p in content_pieces if p.get("content_type") == "ad"]
    if ad_variants:
        if len(ad_variants) < 3:
            results["failed_checks"].append(f"Only {len(ad_variants)} ad variants (need 3)")
        else:
            results["passed_checks"].append(f"Has {len(ad_variants)} ad variants")

    return results


# =============================================================================
# LLM-BASED CHECKS (TIER 1)
# =============================================================================

def run_llm_based_checks(content_pieces: list[dict], brand_context: str) -> dict:
    """Run LLM-based validation checks (TIER 1 - free model)."""
    # TIER 1: Validation task - use free model
    llm = get_tracked_llm("classify", temperature=0.0)

    results = {
        "passed_checks": [],
        "failed_checks": [],
    }

    # Sample first few pieces for LLM validation (cost optimization)
    sample_pieces = content_pieces[:3]

    for piece in sample_pieces:
        copy = piece.get("copy", "")

        # Check: Brand voice consistency
        voice_check_prompt = f"""Does this copy sound like ContentCued brand voice?

Copy: {copy[:500]}

Brand Guidelines (excerpt):
{brand_context[:1000]}

Respond with ONLY "yes" or "no".
"""

        response = llm.invoke([{"role": "user", "content": voice_check_prompt}])
        if "yes" in response.content.lower():
            results["passed_checks"].append(f"{piece['id']}: Brand voice consistent")
        else:
            results["failed_checks"].append(f"{piece['id']}: Brand voice inconsistent")

        # Check: CTA clarity
        cta_check_prompt = f"""Is there a clear call-to-action in this copy?

Copy: {copy[:500]}

Respond with ONLY "yes" or "no".
"""

        response = llm.invoke([{"role": "user", "content": cta_check_prompt}])
        if "yes" in response.content.lower():
            results["passed_checks"].append(f"{piece['id']}: Has clear CTA")
        else:
            results["failed_checks"].append(f"{piece['id']}: CTA unclear")

    return results


# =============================================================================
# QUALITY SCORING
# =============================================================================

def calculate_quality_score(rule_results: dict, llm_results: dict) -> tuple[float, list[str]]:
    """Calculate overall quality score from check results."""

    total_checks = 0
    passed_checks = 0
    issues = []

    # Process rule-based checks
    total_checks += len(rule_results["passed_checks"]) + len(rule_results["failed_checks"])
    passed_checks += len(rule_results["passed_checks"])
    issues.extend([msg for msg in rule_results["failed_checks"] if "Missing" in msg or "Exceeds" in msg])

    # Process LLM-based checks
    total_checks += len(llm_results["passed_checks"]) + len(llm_results["failed_checks"])
    passed_checks += len(llm_results["passed_checks"])
    issues.extend(llm_results["failed_checks"])

    # Calculate score
    if total_checks == 0:
        return 0.0, ["No checks run"]

    score = passed_checks / total_checks

    return score, issues


if __name__ == "__main__":
    print("Quality Agent - validates content against brand guidelines")
    print("Mix of rule-based (zero cost) and TIER 1 LLM checks")
