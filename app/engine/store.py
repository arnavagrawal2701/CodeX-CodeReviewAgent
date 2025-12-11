# app/engine/store.py
from __future__ import annotations

from typing import Dict, Any
from datetime import datetime

from app.engine.models import Graph, State, ExecutionLogEntry


# Simple in-memory stores
GRAPHS: Dict[str, Graph] = {}
RUNS: Dict[str, Dict[str, Any]] = {}


def save_graph(graph: Graph) -> None:
    GRAPHS[graph.id] = graph


def get_graph(graph_id: str) -> Graph:
    graph = GRAPHS.get(graph_id)
    if graph is None:
        raise KeyError(f"Graph '{graph_id}' not found")
    return graph


def create_run(graph_id: str, initial_state: State) -> str:
    run_id = f"run_{len(RUNS) + 1}"
    now = datetime.utcnow().isoformat()
    RUNS[run_id] = {
        "id": run_id,
        "graph_id": graph_id,
        "state": initial_state,
        "log": [],  # list[ExecutionLogEntry]
        "status": "created",
        "created_at": now,
        "updated_at": now,
    }
    return run_id


def update_run(run_id: str, state: State, log: list[ExecutionLogEntry], status: str) -> None:
    if run_id not in RUNS:
        raise KeyError(f"Run '{run_id}' not found")
    RUNS[run_id]["state"] = state
    RUNS[run_id]["log"] = log
    RUNS[run_id]["status"] = status
    RUNS[run_id]["updated_at"] = datetime.utcnow().isoformat()


def get_run(run_id: str) -> Dict[str, Any]:
    run = RUNS.get(run_id)
    if run is None:
        raise KeyError(f"Run '{run_id}' not found")
    return run
