# Lecture 5 Assignment — Tools and Agents

Small coding practice (~20–30 min). Use LangChain tools like in class. Look at `demos/` for patterns. Do **not** edit the demos — write your own scripts in `lecture5/assignment/`.

**Setup:** finish `lecture5/README.md` (venv, install, API key in `demos/.env`).

```python
import sys
sys.path.insert(0, "../demos")
from _client import get_llm
```

---

## Tasks

### Task 1 — One custom `@tool`

Write `task1_my_tool.py`: make **one** tool with `@tool` (for example, echo a service name, or look up a status in a tiny dict). Print the tool’s **name** and **description**. (Demo 1 shows `.name` and `.description`.)

### Task 2 — `bind_tools` chooses a tool

Write `task2_bind_tools.py`: bind your tool (or a tiny copy of Demo 1’s pattern) with `llm.bind_tools(...)`. Ask **one** question. Print which tool was chosen (or that none was). Keep it smaller than Demo 1.

### Task 3 — Add one tool to the agent (optional)

Copy `demos/demo_3_devops_agent.py` into `assignment/`. Add **one new** custom tool. Ask **one** question that needs that new tool. Run your copy.

---

## Submit

Your `.py` files. Do **not** share your API key or `.env`.
