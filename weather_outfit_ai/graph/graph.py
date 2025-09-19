"""
DEPRECATED: This module has been replaced with pure Pydantic orchestration.

The LangGraph-based orchestration has been replaced with a pure Pydantic approach.
See weather_outfit_ai/orchestrator/outfit_orchestrator.py for the new implementation.

This file is kept for reference only and will be removed in a future version.
The original implementation has been moved to graph_deprecated.py.
"""

import warnings

warnings.warn(
    "The graph module is deprecated. Use weather_outfit_ai.orchestrator.outfit_orchestrator instead.",
    DeprecationWarning,
    stacklevel=2
)

# For backward compatibility, you can still import the deprecated function
from .graph_deprecated import create_outfit_graph

__all__ = ["create_outfit_graph"]
