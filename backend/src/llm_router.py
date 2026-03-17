"""
LLM Router

Placeholder for LLM routing and cost tracking.
TODO: Integrate with parent src/llm_router.py
"""

from typing import Dict, Any


# Cost tracking
_cost_tracker: Dict[str, Any] = {
    "total_cost": 0.0,
    "calls": {}
}


def reset_cost_tracker() -> None:
    """Reset the cost tracker."""
    global _cost_tracker
    _cost_tracker = {
        "total_cost": 0.0,
        "calls": {}
    }


def get_cost_tracker() -> Dict[str, Any]:
    """Get the current cost tracker."""
    return _cost_tracker
