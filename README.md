# CodeX — Code Review Agent  
### A Minimal Workflow Engine + Rule-Based Code Analysis System (FastAPI)

**CodeX** is a lightweight, modular, and extensible **workflow engine** designed to demonstrate backend engineering skills, workflow-driven execution, and state-driven logic.
It includes a fully working **Code Review Mini-Agent** that analyzes Python code using a sequence of rule-based workflow nodes.

This project showcases:
- Clean Python architecture  
- FastAPI backend design  
- Stateful workflow graph execution  
- Looping, branching, transitions  
- Clear logs and execution metadata  
- A simple interactive HTML+JS frontend  
- Great readability and code hygiene  
---

# Features

### Workflow Engine (LangGraph-style, minimal)
- Nodes are Python functions  
- Shared mutable state flows between nodes  
- Edges define node → node transitions  
- Supports branching via `_next_node`  
- Loop control via dedicated node  
- Execution log with per-step durations  

### Code Review Mini-Agent
The included workflow (`code_review_v1`) performs:

1. **extract** → Extract function signatures  
2. **complexity** → Estimate complexity from loops & conditionals  
3. **issues** → Detect code smells (long lines, TODOs, temp vars…)  
4. **suggest** → Generate human-friendly suggestions  
5. **evaluate** → Compute a code quality score  
6. **loop** → Repeat until score ≥ threshold  

Everything is rule-based and fully deterministic.

### API Endpoints (FastAPI)
| Method | Path | Description |
|--------|-------|-------------|
| `POST` | `/graph/create` | Register custom workflows |
| `POST` | `/graph/run` | Execute workflow with given state |
| `GET`  | `/graph/state/{run_id}` | Inspect stored runs |
| `GET`  | `/static/app.html` | Interactive UI |
| `GET`  | `/docs` | API documentation |

### Frontend (HTML + JS)
A clean UI that lets you:
- Paste Python code  
- Run CodeX analysis  
- View suggestions  
- View full execution logs  
- Inspect raw engine output state  

No frameworks used — pure HTML/CSS/JS.

---

# Project Structure

```

CodeX/
│
├── app/
│   ├── main.py               # FastAPI entry point
│   ├── api/
│   │   └── graph_routes.py   # REST endpoints
│   ├── engine/
│   │   ├── models.py         # Graph, State, Log models
│   │   ├── executor.py       # Node execution engine
│   │   ├── store.py          # In-memory graph & run storage
│   │   └── registry.py       # Node registry
│   └── workflows/
│       └── code_review.py    # Code Review workflow & nodes
│
├── static/
│   ├── landing.html          # Landing page
│   └── app.html              # Frontend app UI
│
└── requirements.txt

````

---

# Installation

### 1. Clone project

```bash
git clone https://github.com/your-username/CodeX.git
cd CodeX
````

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

### 3. Run server

```bash
uvicorn app.main:app --reload
```

### 4. Open the UI

* **Landing page:**
  [http://127.0.0.1:8000/](http://127.0.0.1:8000/)

* **Application:**
  [http://127.0.0.1:8000/static/app.html](http://127.0.0.1:8000/static/app.html)

* **Swagger API Docs:**
  [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)

---

# How CodeX Works

### Workflow Definition

A graph consists of:

* Node list
* Edge mapping
* Start node
* Max steps
* Node registry lookup

Example snippet:

```python
graph = Graph(
    id="code_review_v1",
    nodes={ "extract": extract_fn, "complexity": complexity_fn, ... },
    edges={
        "extract": "complexity",
        "complexity": "issues",
        "issues": "suggest",
        "suggest": "evaluate",
        "evaluate": "loop",
        "loop": None
    },
    start_node_id="extract",
)
```

### Execution Model

The engine:

1. Executes current node
2. Updates shared `state`
3. Logs the step
4. Chooses next node via:

   * `state["_next_node"]` override, or
   * edge mapping

Loop node can redirect execution backward until a threshold is met.

### Example Output

```json
{
  "run_id": "run_3",
  "final_state": {
    "functions": ["def foo(x):"],
    "issues": ["Line 2: TODO comment present"],
    "quality_score": 95,
    "suggestions": [
      "Complexity looks reasonable for this snippet.",
      "Address the following issues detected:",
      "Line 2: TODO comment present"
    ]
  },
  "log": [
    {"step":1,"node_id":"extract","summary":"functions=1"},
    {"step":2,"node_id":"complexity","summary":"complexity=4"},
    ...
  ],
  "status": "completed"
}
```

---

# UI Overview

The `/static/app.html` UI displays:

* A code editor box
* A **Run Review** button
* A suggestions panel
* A node-by-node execution log
* A raw state panel
* A score pill showing quality score

Built using **zero dependencies**.


---

# 🤝 Contributing

Feel free to submit issues or enhancements.
New workflow examples are especially welcome!

---

# 📄 License

MIT License — free to use, modify, and distribute.

---

# 🎉 Final Note

**CodeX — Code Review Agent** demonstrates backend architecture, workflow orchestration, structured state handling, and clean system design.

---

```

---
