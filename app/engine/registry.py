# app/engine/registry.py
from __future__ import annotations

from typing import Dict

from app.engine.models import NodeCallable

NODE_REGISTRY: Dict[str, NodeCallable] = {}


def register_node(node_id: str, func: NodeCallable) -> None:
    NODE_REGISTRY[node_id] = func


def get_node(node_id: str) -> NodeCallable:
    if node_id not in NODE_REGISTRY:
        raise KeyError(f"Node '{node_id}' not registered")
    return NODE_REGISTRY[node_id]
