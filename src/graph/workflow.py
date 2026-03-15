"""
Main LangGraph Workflow - Campaign Generation StateGraph

Wires all agents together into a complete campaign generation pipeline.
"""

from langgraph.graph import StateGraph, END

from src.state import CampaignState
from src.agents.orchestrator import orchestrator_node
from src.agents.copy_agent import copy_agent_node
from src.agents.visual_agent import visual_agent_node
from src.agents.adapter_agent import adapter_agent_node
from src.agents.quality_agent import quality_agent_node
from src.agents.blog_agent import blog_agent_node
from src.graph.routing import (
    route_after_copy,
    route_after_quality,
    route_after_review,
    human_review_node,
    save_campaign_node,
)


# =============================================================================
# BUILD WORKFLOW
# =============================================================================

def build_campaign_graph() -> StateGraph:
    """
    Build the main campaign generation StateGraph.

    Flow:
        START
        → orchestrator (plan campaign, enrich context)
        → copy_agent (generate all text content)
        → [conditional: blog?] → blog_agent OR visual_agent
        → visual_agent (generate images)
        → adapter_agent (format for platforms)
        → quality_agent (validate everything)
        → [conditional: quality score?] → human_review (INTERRUPT) OR retry
        → [conditional: all approved?] → save_campaign OR copy_agent
        → END
    """
    # Create workflow
    workflow = StateGraph(CampaignState)

    # Add nodes
    workflow.add_node("orchestrator", orchestrator_node)
    workflow.add_node("copy_agent", copy_agent_node)
    workflow.add_node("blog_agent", blog_agent_node)
    workflow.add_node("visual_agent", visual_agent_node)
    workflow.add_node("adapter", adapter_agent_node)
    workflow.add_node("quality", quality_agent_node)
    workflow.add_node("human_review", human_review_node)
    workflow.add_node("save_campaign", save_campaign_node)

    # Entry point
    workflow.set_entry_point("orchestrator")

    # Orchestrator → Copy Agent (always)
    workflow.add_edge("orchestrator", "copy_agent")

    # Copy Agent → conditional: blog or visual
    workflow.add_conditional_edges(
        "copy_agent",
        route_after_copy,
        {
            "blog_agent": "blog_agent",
            "visual_agent": "visual_agent",
        }
    )

    # Blog Agent → Visual Agent
    workflow.add_edge("blog_agent", "visual_agent")

    # Visual Agent → Adapter
    workflow.add_edge("visual_agent", "adapter")

    # Adapter → Quality
    workflow.add_edge("adapter", "quality")

    # Quality → conditional: pass or retry
    workflow.add_conditional_edges(
        "quality",
        route_after_quality,
        {
            "human_review": "human_review",
            "orchestrator": "orchestrator",
            "force_review": "human_review",
        }
    )

    # Human Review → conditional: approve or re-generate
    workflow.add_conditional_edges(
        "human_review",
        route_after_review,
        {
            "save_campaign": "save_campaign",
            "copy_agent": "copy_agent",
        }
    )

    # Save → END
    workflow.add_edge("save_campaign", END)

    return workflow


# =============================================================================
# COMPILE GRAPH
# =============================================================================

def compile_campaign_graph(checkpointer=None, interrupt_before=None):
    """
    Compile the campaign graph with optional persistence and interrupts.

    Args:
        checkpointer: Optional checkpointer for persistence (e.g., SqliteSaver)
        interrupt_before: List of node names to interrupt before

    Returns:
        Compiled runnable graph
    """
    workflow = build_campaign_graph()

    # Compile with checkpointer
    if checkpointer:
        app = workflow.compile(checkpointer=checkpointer)
    else:
        app = workflow.compile()

    return app


# =============================================================================
# CREATE APP WITH PERSISTENCE
# =============================================================================

def create_campaign_app():
    """
    Create the campaign app with in-memory persistence and human-in-the-loop.

    Returns:
        Compiled LangGraph app ready to run
    """
    from langgraph.checkpoint.memory import MemorySaver

    # In-memory checkpointer for persistence
    checkpointer = MemorySaver()

    # Compile with interrupt before human_review
    app = compile_campaign_graph(
        checkpointer=checkpointer,
        interrupt_before=["human_review"]
    )

    return app


if __name__ == "__main__":
    print("ContentCued Campaign Workflow")
    print("=" * 50)
    print("\nBuilding workflow...")

    workflow = build_campaign_graph()

    print("✓ Workflow built successfully")
    print("\nNodes:")
    for node_name in workflow.nodes:
        print(f"  - {node_name}")

    print("\nCreating app with persistence...")
    app = create_campaign_app()
    print("✓ App ready")

    print("\nTo run a campaign, use scripts/run_campaign.py")
