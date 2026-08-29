# Lecture 9 Assignment — StateGraph Fundamentals

Small coding practice (~20–30 min). Use LangGraph like in class. Look at `demos/` for patterns. Do **not** edit the demos — write your own scripts in `lecture9/assignment/`.

**Setup:** finish `lecture9/README.md` (venv, install). Demos 1–2 style work offline; only use `_client` if you add an LLM.

```python
# Only if you need Groq:
import sys
sys.path.insert(0, "../demos")
from _client import get_llm
```

---

## Tasks

### Task 1 — Linear two-node graph

Write `task1_linear_graph.py`:

- Define a `TypedDict` state with at least `service: str` and `notes: list` (use `Annotated[..., operator.add]` like Demo 1).
- Two nodes: `normalize` (lowercase the service) and `tag` (append a note `"tagged:<service>"`).
- Wire `START → normalize → tag → END`, compile, invoke once, print final state.

### Task 2 — Conditional branch

Write `task2_conditional.py`:

- After a `classify` node that sets `env` to `"prod"` or `"dev"` from the service name (your rules),
- Route: `prod` → `needs_approval` node; else → `auto_ok` node.
- Use `add_conditional_edges`. Run **two** invokes (one prod-ish, one dev-ish). Print outcomes.

### Task 3 — Stream one run (optional)

Write `task3_stream.py`: take Task 1 or 2 and print each node update with `stream_mode="updates"` (copy Demo 3's print loop). No LLM required.

---

## Submit

Your `.py` files. Do **not** share your API key or `.env`.
