#!/usr/bin/env python3
"""
Test Individual Agents

Run each agent independently to verify functionality.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from rich.console import Console
from rich.panel import Panel

console = Console()


def test_orchestrator():
    """Test orchestrator agent."""
    console.print("\n[bold cyan]Testing Orchestrator Agent...[/bold cyan]\n")

    from src.agents.orchestrator import orchestrator_node

    test_state = {
        "brief": {
            "product_slug": "chatgpt-plus",
            "audience": "Developers",
            "platforms": ["facebook", "instagram"],
            "tone": "exciting",
        },
        "messages": [],
    }

    result = orchestrator_node(test_state)

    console.print(f"[green]✓ Orchestrator complete[/green]")
    console.print(f"  Campaign Type: {result.get('campaign_type')}")
    console.print(f"  Platforms: {result.get('requested_platforms')}")
    console.print(f"  Product: {result.get('product_info', {}).get('name')}")


def test_copy_agent():
    """Test copy agent."""
    console.print("\n[bold cyan]Testing Copy Agent...[/bold cyan]\n")

    from src.agents.copy_agent import copy_agent_node

    test_state = {
        "product_info": {
            "name": "ChatGPT Plus",
            "price_bdt": 2500,
        },
        "brand_context": "Facebook: Bangla-heavy, emojis",
        "requested_platforms": ["facebook"],
        "campaign_type": "deal_drop",
        "brief": {"audience": "Developers", "tone": "exciting"},
        "execution_plan": {"include_ad_variants": False},
        "messages": [],
        "content_pieces": [],
    }

    result = copy_agent_node(test_state)

    console.print(f"[green]✓ Copy agent complete[/green]")
    console.print(f"  Generated {len(result.get('content_pieces', []))} pieces")


def test_quality_agent():
    """Test quality agent."""
    console.print("\n[bold cyan]Testing Quality Agent...[/bold cyan]\n")

    from src.agents.quality_agent import quality_agent_node

    test_state = {
        "content_pieces": [
            {
                "id": "fb_test",
                "platform": "facebook",
                "copy": "Test copy with ৳2500 price and wa.me link",
                "hashtags": ["#test"],
                "image_paths": ["test.jpg"],
            }
        ],
        "product_info": {"price_bdt": 2500},
        "brand_context": "Test",
        "messages": [],
    }

    result = quality_agent_node(test_state)

    console.print(f"[green]✓ Quality agent complete[/green]")
    console.print(f"  Quality Score: {result.get('quality_score'):.2f}")


def run_all_tests():
    """Run all agent tests."""
    console.print("\n")
    console.print(Panel(
        "[bold cyan]ContentCued Agent Tests[/bold cyan]\n\n"
        "Testing individual agents...",
        title="Agent Test Suite",
        border_style="cyan"
    ))

    tests = [
        ("Orchestrator", test_orchestrator),
        ("Copy Agent", test_copy_agent),
        ("Quality Agent", test_quality_agent),
    ]

    passed = 0
    failed = 0

    for name, test_func in tests:
        try:
            test_func()
            passed += 1
        except Exception as e:
            console.print(f"[red]✗ {name} failed: {e}[/red]")
            failed += 1

    console.print(f"\n[bold]Results: {passed} passed, {failed} failed[/bold]\n")


if __name__ == "__main__":
    try:
        run_all_tests()
    except KeyboardInterrupt:
        console.print("\n[yellow]Tests cancelled[/yellow]")
        sys.exit(0)
