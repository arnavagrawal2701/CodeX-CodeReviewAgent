# app/api/graph_routes.py
from __future__ import annotations

from typing import Dict, Optional, Any

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from app.engine.models import Graph
from app.engine.registry import get_node
from app.engine.store import save_graph, get_graph, create_run, get_run
from app.engine.executor import run_graph

router = APIRouter()


# -------------
# Pydantic models
# -------------


class GraphCreateRequest(BaseModel):
    graph_id: str
    nodes: list[str]
    edges: Dict[str, Optional[str]]
    start_node: str
    max_steps: int = 100


class GraphCreateResponse(BaseModel):
    graph_id: str
    message: str


class GraphRunRequest(BaseModel):
    graph_id: str
    initial_state: Dict[str, Any]


class GraphRunResponse(BaseModel):
    run_id: str
    final_state: Dict[str, Any]
    log: list[Dict[str, Any]]
    status: str


class GraphRunStateResponse(BaseModel):
    run_id: str
    graph_id: str
    state: Dict[str, Any]
    log: list[Dict[str, Any]]
    status: str


# -------------
# Routes
# -------------


@router.post("/create", response_model=GraphCreateResponse)
def create_graph(payload: GraphCreateRequest):
    """
    Create a new graph.

    NOTE: For this assignment, we only allow using pre-registered node IDs
    (like 'extract', 'complexity', etc.). The nodes themselves are Python
    functions stored in a registry.
    """
    # Validate that all nodes exist in registry
    node_funcs = {}
    for node_id in payload.nodes:
        try:
            node_funcs[node_id] = get_node(node_id)
        except KeyError:
            raise HTTPException(
                status_code=400,
                detail=f"Node '{node_id}' is not registered. Register it in a workflow module first.",
            )

    if payload.start_node not in node_funcs:
        raise HTTPException(
            status_code=400,
            detail=f"start_node '{payload.start_node}' must be in 'nodes'",
        )

    graph = Graph(
        id=payload.graph_id,
        nodes=node_funcs,
        edges=payload.edges,
        start_node_id=payload.start_node,
        max_steps=payload.max_steps,
    )

    save_graph(graph)

    return GraphCreateResponse(
        graph_id=payload.graph_id,
        message="Graph created successfully",
    )


@router.post("/run", response_model=GraphRunResponse)
def run_graph_endpoint(payload: GraphRunRequest):
    """
    Run an existing graph synchronously and persist the run.
    """
    try:
        graph = get_graph(payload.graph_id)
    except KeyError:
        raise HTTPException(
            status_code=404,
            detail=f"Graph '{payload.graph_id}' not found",
        )

    # Normal run: persists to RUNS store
    run_id = create_run(graph.id, payload.initial_state)
    final_state, log = run_graph(graph, payload.initial_state, run_id=run_id)
    run_record = get_run(run_id)

    return GraphRunResponse(
        run_id=run_id,
        final_state=final_state,
        log=log,
        status=run_record["status"],
    )


@router.get("/state/{run_id}", response_model=GraphRunStateResponse)
def get_run_state(run_id: str):
    """
    Get current state + log of a given run.
    """
    try:
        run_record = get_run(run_id)
    except KeyError:
        raise HTTPException(
            status_code=404,
            detail=f"Run '{run_id}' not found",
        )

    return GraphRunStateResponse(
        run_id=run_record["id"],
        graph_id=run_record["graph_id"],
        state=run_record["state"],
        log=run_record["log"],
        status=run_record["status"],
    )
