# app/engine/executor.py
from __future__ import annotations

import time
from typing import Tuple, List, Optional

from app.engine.models import Graph, State, ExecutionLogEntry
from app.engine.store import update_run


def _summarise_state(state: State) -> str:
    parts = []
    if "quality_score" in state:
        parts.append(f"quality_score={state['quality_score']}")
    if "iteration" in state:
        parts.append(f"iteration={state['iteration']}")
    if "issues" in state and isinstance(state["issues"], list):
        parts.append(f"issues={len(state['issues'])}")
    if "complexity_report" in state:
        cr = state["complexity_report"]
        est = cr.get("estimated_complexity")
        fn_count = cr.get("function_count")
        if est is not None:
            parts.append(f"complexity={est}")
        if fn_count is not None:
            parts.append(f"functions={fn_count}")
    return ", ".join(parts) or "state updated"


def run_graph(graph: Graph, initial_state: State, run_id: Optional[str] = None) -> Tuple[State, List[ExecutionLogEntry]]:
    """
    Execute a graph synchronously from its start node until completion.
    Supports:
    - default edges
    - optional override: state["_next_node"]
    - termination: no next node OR state["_finished"] is True
    """
    state: State = dict(initial_state)  # copy to avoid mutating caller
    state.setdefault("iteration", 0)
    log: List[ExecutionLogEntry] = []

    current_node_id = graph.start_node_id
    step = 0

    status = "running"

    while current_node_id is not None and step < graph.max_steps:
        step += 1
        node = graph.nodes[current_node_id]

        start_time = time.perf_counter()
        state = node(state)  # node mutates and/or returns new state
        duration_ms = (time.perf_counter() - start_time) * 1000.0

        entry: ExecutionLogEntry = {
            "step": step,
            "node_id": current_node_id,
            "duration_ms": duration_ms,
            "summary": _summarise_state(state),
        }
        log.append(entry)

        # Update run status mid-flight if run_id is provided
        if run_id is not None:
            update_run(run_id, state, log, status)

        # Check for termination flag
        if state.get("_finished"):
            status = "completed"
            break

        # Check for explicit next node override
        next_node_override = state.pop("_next_node", None)
        if next_node_override is not None:
            current_node_id = next_node_override
        else:
            # Default edge-based transition
            current_node_id = graph.edges.get(current_node_id)

    else:
        # loop ended by max_steps or no current_node
        status = "completed" if current_node_id is None else "max_steps_reached"

    if run_id is not None:
        update_run(run_id, state, log, status)

    return state, log
