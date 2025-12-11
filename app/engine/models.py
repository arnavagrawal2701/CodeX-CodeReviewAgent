# app/engine/models.py
from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Callable, Dict, List, Optional, TypedDict


State = Dict[str, Any]
NodeCallable = Callable[[State], State]


class ExecutionLogEntry(TypedDict):
    step: int
    node_id: str
    duration_ms: float
    summary: str


@dataclass
class Graph:
    """
    In-memory representation of a workflow graph.
    """
    id: str
    nodes: Dict[str, NodeCallable]        # node_id -> function
    edges: Dict[str, Optional[str]]       # node_id -> next_node_id (or None to stop)
    start_node_id: str
    max_steps: int = 100
