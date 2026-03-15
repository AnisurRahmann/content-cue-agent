"""
Test LLM Router - Tiered Model Routing
"""

import pytest
from src.llm_router import get_tier1_llm, get_tier2_llm, get_tier3_llm, get_llm_for_task


def test_get_tier1_llm():
    """Test Tier 1 LLM retrieval."""
    try:
        llm = get_tier1_llm()
        assert llm is not None
        print("✓ Tier 1 LLM accessible")
    except ValueError as e:
        if "GROQ_API_KEY" in str(e):
            pytest.skip("GROQ_API_KEY not set")
        raise


def test_get_tier2_llm():
    """Test Tier 2 LLM retrieval."""
    try:
        llm = get_tier2_llm()
        assert llm is not None
        print("✓ Tier 2 LLM accessible")
    except ValueError as e:
        if "DEEPSEEK_API_KEY" in str(e):
            pytest.skip("DEEPSEEK_API_KEY not set")
        raise


def test_get_tier3_llm():
    """Test Tier 3 LLM retrieval."""
    try:
        llm = get_tier3_llm()
        assert llm is not None
        print("✓ Tier 3 LLM accessible")
    except ValueError as e:
        if "ANTHROPIC_API_KEY" in str(e):
            pytest.skip("ANTHROPIC_API_KEY not set")
        raise


def test_task_routing():
    """Test task-based routing."""
    # Tier 1 tasks
    llm = get_llm_for_task("route")
    assert llm is not None

    # Tier 2 tasks
    llm = get_llm_for_task("generate")
    assert llm is not None

    print("✓ Task routing works")


if __name__ == "__main__":
    print("Running LLM Router Tests...")
    test_get_tier1_llm()
    test_task_routing()
    print("\n✓ All tests passed!")
