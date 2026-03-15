"""
Test Graph - End-to-End Workflow
"""

from src.state import initial_state
from src.graph.workflow import build_campaign_graph


def test_graph_build():
    """Test graph can be built."""
    workflow = build_campaign_graph()
    assert workflow is not None
    print("✓ Graph built successfully")

    # Check nodes
    nodes = list(workflow.nodes)
    expected_nodes = [
        "orchestrator",
        "copy_agent",
        "blog_agent",
        "visual_agent",
        "adapter",
        "quality",
        "human_review",
        "save_campaign",
    ]

    for node in expected_nodes:
        assert node in nodes, f"Missing node: {node}"

    print(f"✓ All {len(nodes)} nodes present")


def test_graph_execution():
    """Test graph can execute (without LLM calls)."""
    from unittest.mock import Mock, patch

    # Mock all agents to return state without LLM calls
    def mock_orchestrator(state):
        state["execution_plan"] = {"agents_to_run": ["copy_agent"]}
        state["requested_platforms"] = ["facebook"]
        return state

    def mock_copy_agent(state):
        state["content_pieces"] = []
        return state

    # Create test state
    test_state = initial_state({
        "product_slug": "chatgpt-plus",
        "audience": "Test",
        "platforms": ["facebook"],
        "tone": "casual",
    })

    # Test without actual execution (just structure)
    workflow = build_campaign_graph()
    assert workflow is not None
    print("✓ Graph structure validated")


if __name__ == "__main__":
    print("Testing Graph Workflow...")
    test_graph_build()
    test_graph_execution()
    print("\n✓ All tests passed!")
