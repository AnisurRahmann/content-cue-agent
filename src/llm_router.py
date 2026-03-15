"""
Tiered LLM Router with Cost Tracking

This module provides intelligent routing of LLM calls to different tiers based on:
1. Task type (routing, generation, polish)
2. Cost optimization (free → cheap → quality)
3. Fallback behavior (if provider fails)

Every LLM call in the system MUST go through this router for cost tracking.
"""

import os
from typing import Optional, Literal
from dataclasses import dataclass, field
from datetime import datetime
from dotenv import load_dotenv

from langchain_core.language_models import BaseChatModel
from langchain_groq import ChatGroq
from langchain_anthropic import ChatAnthropic
from langchain_openai import ChatOpenAI

load_dotenv()


# =============================================================================
# COST TRACKING
# =============================================================================

@dataclass
class LLMMCallLog:
    """Record of a single LLM call for cost tracking."""
    timestamp: str
    model_name: str
    tier: str
    task_type: str
    tokens_in: int
    tokens_out: int
    estimated_cost_usd: float


class CostTracker:
    """
    Tracks cumulative token usage and estimated cost per campaign.

    Logs: model_name, tokens_in, tokens_out, estimated_cost, task_type
    Prints summary at end of each campaign run.
    """

    def __init__(self):
        self.calls: list[LLMMCallLog] = []

    def log(
        self,
        model_name: str,
        tier: str,
        task_type: str,
        tokens_in: int,
        tokens_out: int,
        estimated_cost: float,
    ) -> None:
        """Log an LLM call."""
        self.calls.append(LLMMCallLog(
            timestamp=datetime.now().isoformat(),
            model_name=model_name,
            tier=tier,
            task_type=task_type,
            tokens_in=tokens_in,
            tokens_out=tokens_out,
            estimated_cost_usd=estimated_cost,
        ))

    def get_summary(self) -> dict:
        """Get cost summary by tier."""
        summary = {
            "total_calls": len(self.calls),
            "total_cost": sum(c.estimated_cost_usd for c in self.calls),
            "total_tokens_in": sum(c.tokens_in for c in self.calls),
            "total_tokens_out": sum(c.tokens_out for c in self.calls),
            "by_tier": {
                "tier_1": {"calls": 0, "cost": 0.0, "tokens_in": 0, "tokens_out": 0},
                "tier_2": {"calls": 0, "cost": 0.0, "tokens_in": 0, "tokens_out": 0},
                "tier_3": {"calls": 0, "cost": 0.0, "tokens_in": 0, "tokens_out": 0},
            },
        }

        for call in self.calls:
            tier_key = call.tier
            summary["by_tier"][tier_key]["calls"] += 1
            summary["by_tier"][tier_key]["cost"] += call.estimated_cost_usd
            summary["by_tier"][tier_key]["tokens_in"] += call.tokens_in
            summary["by_tier"][tier_key]["tokens_out"] += call.tokens_out

        return summary

    def print_report(self) -> None:
        """Print a formatted cost report."""
        from rich.console import Console
        from rich.table import Table

        console = Console()
        summary = self.get_summary()

        # Title
        console.print("\n[bold cyan]╔══════════════════════════════════════════╗[/bold cyan]")
        console.print("[bold cyan]║      CAMPAIGN COST REPORT                 ║[/bold cyan]")
        console.print("[bold cyan]╚══════════════════════════════════════════╝[/bold cyan]\n")

        # Summary table
        table = Table(title="Cost Summary by Tier", show_header=True, header_style="bold magenta")
        table.add_column("Tier", style="cyan", width=10)
        table.add_column("Calls", justify="right", style="green")
        table.add_column("Tokens In", justify="right", style="blue")
        table.add_column("Tokens Out", justify="right", style="blue")
        table.add_column("Cost", justify="right", style="yellow")

        tier_names = {"tier_1": "TIER 1 (Free)", "tier_2": "TIER 2 (Cheap)", "tier_3": "TIER 3 (Quality)"}
        for tier_key, data in summary["by_tier"].items():
            if data["calls"] > 0:
                table.add_row(
                    tier_names[tier_key],
                    str(data["calls"]),
                    f"{data['tokens_in']:,}",
                    f"{data['tokens_out']:,}",
                    f"${data['cost']:.4f}",
                )

        console.print(table)

        # Total
        console.print(f"\n[bold]Total Calls:[/bold] {summary['total_calls']}")
        console.print(f"[bold]Total Cost:[/bold] ${summary['total_cost']:.4f}")
        console.print(f"[bold]Total Tokens:[/bold] {summary['total_tokens_in'] + summary['total_tokens_out']:,}\n")

        # Savings estimate
        if summary["by_tier"]["tier_1"]["calls"] > 0:
            tier_1_cost = summary["by_tier"]["tier_1"]["cost"]
            console.print(f"[green]✓ Used {summary['by_tier']['tier_1']['calls']} free Tier 1 calls (~${tier_1_cost:.4f} savings)[/green]")
        if summary["by_tier"]["tier_2"]["calls"] > 0:
            console.print(f"[green]✓ Used {summary['by_tier']['tier_2']['calls']} cheap Tier 2 calls instead of quality tier[/green]")


# Global cost tracker instance
_cost_tracker = CostTracker()


def get_cost_tracker() -> CostTracker:
    """Get the global cost tracker instance."""
    return _cost_tracker


def reset_cost_tracker() -> None:
    """Reset the cost tracker (call at start of new campaign)."""
    global _cost_tracker
    _cost_tracker = CostTracker()


# =============================================================================
# LLM PROVIDER CONFIGURATION
# =============================================================================

# Cost per million tokens (input / output)
# Source: Provider pricing as of 2025
COST_PER_MILLION = {
    # Tier 1: Groq (Free for Llama 3.3 70B during beta)
    "groq/llama-3.3-70b": (0.0, 0.0),
    # Tier 2: DeepSeek V3
    "deepseek/deepseek-chat": (0.27, 1.10),  # $0.27/M input, $1.10/M output
    # Tier 3: Claude Sonnet 4
    "claude/claude-sonnet-4": (3.0, 15.0),  # $3.0/M input, $15.0/M output
}


def estimate_cost(model_name: str, tokens_in: int, tokens_out: int) -> float:
    """Estimate cost in USD for a given model and token usage."""
    if model_name not in COST_PER_MILLION:
        return 0.0

    cost_in, cost_out = COST_PER_MILLION[model_name]
    return (tokens_in * cost_in / 1_000_000) + (tokens_out * cost_out / 1_000_000)


# =============================================================================
# TIERED LLM GETTERS
# =============================================================================

def get_tier1_llm(temperature: float = 0.0) -> BaseChatModel:
    """
    TIER 1: Free/Cheap — routing, classification, extraction, reformatting.
    ~70-80% of calls. Target: $0/campaign (Groq free) or <$0.001/call.

    Models: Groq Llama 3.3 70B (free during beta)
    """
    provider = os.getenv("TIER1_PROVIDER", "groq").lower()

    if provider == "groq":
        api_key = os.getenv("GROQ_API_KEY")
        if not api_key:
            raise ValueError("GROQ_API_KEY not set. Tier 1 requires Groq API key.")

        model = ChatGroq(
            model="llama-3.3-70b-versatile",
            api_key=api_key,
            temperature=temperature,
        )
        model._cost_model_name = "groq/llama-3.3-70b"
        model._tier = "tier_1"
        return model
    else:
        raise ValueError(f"Unsupported Tier 1 provider: {provider}")


def get_tier2_llm(temperature: float = 0.7) -> BaseChatModel:
    """
    TIER 2: Cheap — content generation, drafts, translations.
    ~15-25% of calls. Target: <$0.01/call.

    Models: DeepSeek V3 ($0.28/MTok)
    Falls back to Tier 1 if API key not set.
    """
    provider = os.getenv("TIER2_PROVIDER", "deepseek").lower()

    if provider == "deepseek":
        api_key = os.getenv("DEEPSEEK_API_KEY")
        if not api_key:
            # Fall back to Tier 1
            from rich import print as rprint
            rprint("[yellow]⚠ DEEPSEEK_API_KEY not set. Falling back to Tier 1 for this call.[/yellow]")
            return get_tier1_llm(temperature=temperature)

        model = ChatOpenAI(
            model="deepseek-chat",
            api_key=api_key,
            base_url="https://api.deepseek.com/v1",
            temperature=temperature,
        )
        model._cost_model_name = "deepseek/deepseek-chat"
        model._tier = "tier_2"
        return model
    else:
        raise ValueError(f"Unsupported Tier 2 provider: {provider}")


def get_tier3_llm(temperature: float = 0.7) -> BaseChatModel:
    """
    TIER 3: Quality — final polish, complex creative.
    ≤5% of calls. Target: <$0.05/call.

    Models: Claude Sonnet 4
    Falls back to Tier 2, then Tier 1 if API key not set.
    """
    provider = os.getenv("TIER3_PROVIDER", "claude").lower()

    if provider == "claude":
        api_key = os.getenv("ANTHROPIC_API_KEY")
        if not api_key:
            # Fall back to Tier 2
            from rich import print as rprint
            rprint("[yellow]⚠ ANTHROPIC_API_KEY not set. Falling back to Tier 2 for this call.[/yellow]")
            return get_tier2_llm(temperature=temperature)

        model = ChatAnthropic(
            model="claude-sonnet-4-20250514",
            api_key=api_key,
            temperature=temperature,
        )
        model._cost_model_name = "claude/claude-sonnet-4"
        model._tier = "tier_3"
        return model
    else:
        raise ValueError(f"Unsupported Tier 3 provider: {provider}")


# =============================================================================
# TASK-BASED ROUTING
# =============================================================================

TaskType = Literal[
    # Tier 1 tasks
    "route",
    "classify",
    "extract",
    "format",
    # Tier 2 tasks
    "generate",
    "translate",
    "draft",
    "rewrite",
    # Tier 3 tasks
    "polish",
    "complex_creative",
    "escalate",
]


def get_llm_for_task(task_type: TaskType, temperature: float = 0.0) -> BaseChatModel:
    """
    Auto-routes to correct tier based on task type.

    Tier 1: 'route' | 'classify' | 'extract' | 'format'
    Tier 2: 'generate' | 'translate' | 'draft' | 'rewrite'
    Tier 3: 'polish' | 'complex_creative' | 'escalate'
    """
    # Tier 1 tasks
    if task_type in ("route", "classify", "extract", "format"):
        return get_tier1_llm(temperature=temperature)

    # Tier 2 tasks
    if task_type in ("generate", "translate", "draft", "rewrite"):
        return get_tier2_llm(temperature=temperature)

    # Tier 3 tasks
    if task_type in ("polish", "complex_creative", "escalate"):
        return get_tier3_llm(temperature=temperature)

    raise ValueError(f"Unknown task type: {task_type}")


# =============================================================================
# WRAPPED LLM CALL WITH COST TRACKING
# =============================================================================

from langchain_core.messages import BaseMessage
from langchain_core.callbacks import CallbackManagerForLLMRun


class TrackedLLM:
    """
    Wrapper that automatically tracks cost for every LLM call.

    Usage:
        llm = get_tracked_llm("generate")  # Auto-routes to Tier 2
        response = llm.invoke(messages)    # Automatically tracked
    """

    def __init__(self, task_type: TaskType, temperature: float = 0.0):
        self._task_type = task_type
        self._temperature = temperature
        self._llm = get_llm_for_task(task_type, temperature)
        self._model_name = getattr(self._llm, "_cost_model_name", "unknown")
        self._tier = getattr(self._llm, "_tier", "unknown")

    def invoke(self, messages: list[BaseMessage], **kwargs) -> BaseMessage:
        """Invoke the LLM and track cost."""
        # Get response with usage metadata
        response = self._llm.invoke(messages, **kwargs)

        # Extract token usage if available
        tokens_in = 0
        tokens_out = 0

        if hasattr(response, "usage_metadata"):
            usage = response.usage_metadata
            if usage:
                tokens_in = usage.get("input_tokens", 0)
                tokens_out = usage.get("output_tokens", 0)

        # Estimate and log cost
        estimated_cost = estimate_cost(self._model_name, tokens_in, tokens_out)
        get_cost_tracker().log(
            model_name=self._model_name,
            tier=self._tier,
            task_type=self._task_type,
            tokens_in=tokens_in,
            tokens_out=tokens_out,
            estimated_cost=estimated_cost,
        )

        return response

    @property
    def model_name(self) -> str:
        return self._model_name

    @property
    def tier(self) -> str:
        return self._tier


def get_tracked_llm(task_type: TaskType, temperature: float = 0.0) -> TrackedLLM:
    """
    Get an LLM instance that automatically tracks cost.

    This is the RECOMMENDED way to get LLMs in agents.

    Example:
        llm = get_tracked_llm("generate")  # For copy generation (Tier 2)
        llm = get_tracked_llm("route")     # For routing (Tier 1)
        llm = get_tracked_llm("polish")    # For final polish (Tier 3)
    """
    return TrackedLLM(task_type, temperature)
