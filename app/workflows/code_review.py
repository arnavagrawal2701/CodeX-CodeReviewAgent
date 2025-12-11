# app/workflows/code_review.py
from __future__ import annotations

from typing import List

from app.engine.models import Graph, State
from app.engine.registry import register_node
from app.engine.store import save_graph


QUALITY_THRESHOLD = 80
MAX_ITERATIONS = 3
DEFAULT_GRAPH_ID = "code_review_v1"


# ----------------------
# Node implementations
# ----------------------


def extract_functions(state: State) -> State:
    """
    Very naive 'function extraction':
    - Find lines starting with 'def '
    - Save their signatures in state["functions"]
    """
    code: str = state.get("code", "")
    functions: List[str] = []

    for line in code.splitlines():
        striped = line.strip()
        if striped.startswith("def "):
            # Take the whole line as function signature
            functions.append(striped)

    state["functions"] = functions
    return state


def check_complexity(state: State) -> State:
    """
    Simple 'complexity' heuristic:
    - Base complexity = number of functions
    - + 1 for each 'for' or 'while'
    - + 2 for each 'if'
    """
    code: str = state.get("code", "")
    functions: List[str] = state.get("functions", [])

    complexity = len(functions)

    for line in code.splitlines():
        stripped = line.strip()
        if stripped.startswith("for ") or stripped.startswith("while "):
            complexity += 1
        if " if " in f" {stripped} " or stripped.startswith("if "):
            complexity += 2

    state["complexity_report"] = {
        "estimated_complexity": complexity,
        "function_count": len(functions),
    }
    return state


def detect_issues(state: State) -> State:
    """
    Very basic code smell detector:
    - Line > 100 chars
    - 'TODO' in code
    - variables named 'temp'
    """
    code: str = state.get("code", "")
    issues: List[str] = []

    for i, line in enumerate(code.splitlines(), start=1):
        if len(line) > 100:
            issues.append(f"Line {i}: line too long (>100 chars)")
        if "TODO" in line:
            issues.append(f"Line {i}: TODO comment present")
        if "temp" in line:
            issues.append(f"Line {i}: variable name 'temp' used")

    state["issues"] = issues
    return state


def suggest_improvements(state: State) -> State:
    """
    Generate human-readable suggestions from issues + complexity.
    """
    issues: List[str] = state.get("issues", [])
    complexity_report = state.get("complexity_report", {})
    complexity = complexity_report.get("estimated_complexity", 0)

    suggestions: List[str] = []

    if complexity > 15:
        suggestions.append(
            "Overall complexity is high. Consider splitting large functions into smaller ones."
        )
    elif complexity > 8:
        suggestions.append(
            "Complexity is moderate. Look for opportunities to simplify nested conditions or loops."
        )
    else:
        suggestions.append("Complexity looks reasonable for this snippet.")

    if issues:
        suggestions.append("Address the following issues detected:")
        suggestions.extend(issues)
    else:
        suggestions.append("No obvious issues detected. Good job!")

    state["suggestions"] = suggestions
    return state


def evaluate_quality(state: State) -> State:
    """
    Compute a simple quality score based on:
    - complexity
    - number of issues
    """
    complexity_report = state.get("complexity_report", {})
    complexity = complexity_report.get("estimated_complexity", 0)
    issues: List[str] = state.get("issues", [])

    # Start from 100, subtract penalties
    score = 100
    score -= max(0, (complexity - 5) * 3)
    score -= len(issues) * 5
    score = max(0, min(100, score))  # clamp 0-100

    state["quality_score"] = score

    # keep a small history
    history: List[int] = state.get("score_history", [])
    history.append(score)
    state["score_history"] = history

    return state


def loop_decider(state: State) -> State:
    """
    Decide if we should loop again or finish.

    - If quality_score >= QUALITY_THRESHOLD -> _finished = True
    - Else, if iteration < MAX_ITERATIONS -> increment iteration and go back to 'extract'
    - Else -> finish anyway (to avoid infinite loop)
    """
    score: int = state.get("quality_score", 0)
    iteration: int = state.get("iteration", 0)

    if score >= QUALITY_THRESHOLD:
        # Done!
        state["_finished"] = True
        return state

    if iteration + 1 < MAX_ITERATIONS:
        # Loop again from extract
        state["iteration"] = iteration + 1
        state["_next_node"] = "extract"
        return state

    # Safety stop
    state["_finished"] = True
    return state


# ----------------------
# Graph registration
# ----------------------


def register_default_workflow() -> None:
    """
    Register nodes in the global registry and create
    the default 'code_review_v1' graph.
    """
    # Register nodes
    register_node("extract", extract_functions)
    register_node("complexity", check_complexity)
    register_node("issues", detect_issues)
    register_node("suggest", suggest_improvements)
    register_node("evaluate", evaluate_quality)
    register_node("loop", loop_decider)

    # Build the graph (nodes dict uses direct callables)
    nodes = {
        "extract": extract_functions,
        "complexity": check_complexity,
        "issues": detect_issues,
        "suggest": suggest_improvements,
        "evaluate": evaluate_quality,
        "loop": loop_decider,
    }

    edges = {
        "extract": "complexity",
        "complexity": "issues",
        "issues": "suggest",
        "suggest": "evaluate",
        "evaluate": "loop",
        "loop": None,  # loop_decider will either set _next_node or finish
    }

    graph = Graph(
        id=DEFAULT_GRAPH_ID,
        nodes=nodes,
        edges=edges,
        start_node_id="extract",
        max_steps=50,
    )

    save_graph(graph)
