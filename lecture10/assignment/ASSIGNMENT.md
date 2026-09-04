# Lecture 10 Assignment — Manual ReAct

Small coding practice (~25–35 min). Look at `demos/`. Do **not** edit the demos — write scripts in `lecture10/assignment/`.

**Setup:** finish `lecture10/README.md` (venv, install, `demos/.env`).

```python
import sys
sys.path.insert(0, "../demos")
from _client import get_llm
```

**Theme tip:** Use an HR / IT / expense fake lookup (same style as the demos). Avoid food examples.

---

## Tasks

### Task 1 — One `@tool` + ToolNode once

Write `task1_toolnode_once.py`: define one workplace `@tool` (fake dict lookup is fine — e.g. leave balance or ticket status). Bind it, ask one question that should call it, run `ToolNode` once, print the `ToolMessage`.

### Task 2 — Tiny ReAct graph

Write `task2_mini_react.py`: `MessagesState` graph with `agent` + `tools` + `tools_condition` + edge `tools → agent`. Ask one question. Print the final answer.

### Task 3 — Contrast note (optional)

Write `task3_contrast.md` (5–8 lines): when would you keep `create_agent` vs open a hand-built ReAct graph? Use L10 Demo 3 language (LangChain API vs LangGraph engine; HITL / custom gates → hand graph).

---

## Submit

Your files. Do **not** share `.env` / API keys.
