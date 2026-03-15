#!/usr/bin/env python3
"""
Interactive CLI Runner for Campaign Generation

Run campaigns end-to-end with human-in-the-loop approval.
Works independently without the dashboard.

Usage:
    python scripts/run_campaign.py
"""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from rich.console import Console
from rich.panel import Panel
from rich.prompt import Prompt, Confirm
from rich.table import Table

from src.state import initial_state
from src.graph.workflow import create_campaign_app
from src.llm_router import reset_cost_tracker


console = Console()


def get_campaign_brief() -> dict:
    """Get campaign brief from user input."""
    console.print("\n[bold cyan]Create New Campaign[/bold cyan]\n")

    product = Prompt.ask(
        "Product slug",
        choices=["chatgpt-plus", "gemini-pro", "midjourney", "canva-pro",
                 "capcut-pro", "grammarly-premium", "microsoft-365",
                 "perplexity-pro", "cursor-pro", "adobe-creative-cloud"],
        default="chatgpt-plus"
    )

    audience = Prompt.ask("Target audience", default="Developers and content creators")

    # Platform selection
    console.print("\nSelect platforms (comma-separated):")
    console.print("  facebook, instagram, linkedin, whatsapp, blog")
    platforms_input = Prompt.ask("Platforms", default="facebook, instagram, linkedin, whatsapp")
    platforms = [p.strip() for p in platforms_input.split(",") if p.strip()]

    tone = Prompt.ask(
        "Tone",
        choices=["casual", "professional", "exciting", "informative"],
        default="exciting"
    )

    instructions = Prompt.ask("Special instructions (optional)", default="")

    return {
        "product_slug": product,
        "audience": audience,
        "platforms": platforms,
        "tone": tone,
        "instructions": instructions,
    }


def display_messages(messages: list):
    """Display execution messages."""
    for msg in messages:
        if msg.startswith("✓"):
            console.print(f"[green]{msg}[/green]")
        elif msg.startswith("⚠️"):
            console.print(f"[yellow]{msg}[/yellow]")
        elif msg.startswith("🎯"):
            console.print(f"[cyan]{msg}[/cyan]")
        elif msg.startswith("✍️"):
            console.print(f"[blue]{msg}[/blue]")
        elif msg.startswith("🎨"):
            console.print(f"[magenta]{msg}[/magenta]")
        elif msg.startswith("🔧"):
            console.print(f"[dim]{msg}[/dim]")
        elif msg.startswith("✓"):
            console.print(f"[green]{msg}[/green]")
        else:
            console.print(msg)


def display_content_pieces(state: dict):
    """Display generated content pieces for review."""
    content_pieces = state.get("content_pieces", [])

    if not content_pieces:
        console.print("[yellow]No content pieces to review[/yellow]")
        return {}

    console.print(f"\n[bold]Generated Content ({len(content_pieces)} pieces)[/bold]\n")

    decisions = {}

    for i, piece in enumerate(content_pieces):
        console.print(Panel(
            f"[bold]{piece['platform'].upper()} - {piece['content_type']}[/bold]\n\n"
            f"{piece['copy']}\n\n"
            f"[dim]Hashtags: {', '.join(piece.get('hashtags', []))}[/dim]\n"
            f"[dim]CTA: {piece.get('cta_link', 'N/A')}[/dim]",
            title=f"[{i+1}/{len(content_pieces)}] {piece['id']}",
            border_style="blue"
        ))

        action = Prompt.ask(
            "Action",
            choices=["approve", "reject", "edit"],
            default="approve"
        )

        if action == "approve":
            decisions[piece['id']] = {"action": "approve"}
        elif action == "reject":
            feedback = Prompt.ask("Feedback (why reject?)", default="")
            decisions[piece['id']] = {"action": "reject", "feedback": feedback}
        elif action == "edit":
            console.print("[dim]Edit not implemented in CLI - use dashboard[/dim]")
            decisions[piece['id']] = {"action": "approve"}

    return decisions


def run_campaign():
    """Run complete campaign workflow."""
    console.print("\n")
    console.print(Panel(
        "[bold cyan]ContentCued Marketing Agent[/bold cyan]\n\n"
        "Multi-agent campaign generation with tiered LLM routing",
        title="Welcome",
        border_style="cyan"
    ))

    # Reset cost tracker
    reset_cost_tracker()

    # Get brief
    brief = get_campaign_brief()

    # Create initial state
    state = initial_state(brief)

    # Create app
    app = create_campaign_app()

    # Run workflow until human review
    console.print("\n[bold]Generating campaign...[/bold]\n")

    config = {"configurable": {"thread_id": "campaign_cli_001"}}
    result = app.invoke(state, config=config)

    # Display progress
    display_messages(result.get("messages", []))

    # Display quality score
    quality_score = result.get("quality_score", 0)
    console.print(f"\n[bold]Quality Score: {quality_score:.2f}[/bold]")

    if result.get("quality_issues"):
        console.print(f"[yellow]Issues: {', '.join(result['quality_issues'][:5])}[/yellow]")

    # Human review
    console.print("\n" + "=" * 50)
    console.print("[bold]HUMAN REVIEW[/bold]")
    console.print("=" * 50)

    decisions = display_content_pieces(result)

    # Update state and continue
    result["human_decisions"] = decisions

    console.print("\n[bold]Finalizing campaign...[/bold]\n")

    # Continue workflow
    result = app.invoke(result, config=config)

    # Display final messages
    display_messages(result.get("messages", []))

    console.print("\n[bold green]✓ Campaign complete![/bold green]\n")


if __name__ == "__main__":
    try:
        run_campaign()
    except KeyboardInterrupt:
        console.print("\n\n[yellow]Campaign cancelled by user[/yellow]")
        sys.exit(0)
    except Exception as e:
        console.print(f"\n\n[red]Error: {e}[/red]")
        import traceback
        traceback.print_exc()
        sys.exit(1)
