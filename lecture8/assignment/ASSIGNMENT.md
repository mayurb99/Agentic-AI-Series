# Lecture 8 Assignment — On-call runbook helper

Small coding practice (~30–40 min). Extend the **on-call helper** — do **not** only open the UI. Look at `ingest.py`, `agent.py`, and `app.py`. Do **not** edit those files — write your own scripts in `lecture8/assignment/`.

**Setup:** finish `lecture8/README.md` (venv, install, `.env`, then `python ingest.py`).

```python
import sys
sys.path.insert(0, "..")
from agent import build_chat_agent, ask_chat, TOOLS, search_runbooks
```

---

## Tasks

### Task 1 — Add one new `@tool`

Write `task1_new_tool.py`:

1. Copy the tool pattern from `agent.py`.
2. Add **one new** custom tool (examples: `list_services()` that returns known service names, or `list_log_files()` that lists names under `data/logs/`).
3. Build a **new** `create_agent` that includes the existing tools **plus** your tool (you may copy tool functions into your file — do not import-edit `agent.py`).
4. Ask **one** question that needs your new tool. Print the answer.

### Task 2 — Prove `thread_id` memory yourself

Write `task2_memory_proof.py`:

1. Build a chat agent with `InMemorySaver` (run `ingest.py` first so Chroma exists).
2. On thread `A`, tell the agent your name (or a fake pager handle).
3. On thread `A`, ask "What is my name?" and print the answer.
4. On thread `B`, ask the same question and print the answer.
5. Add a short comment at the bottom of the file explaining why A and B differ.

### Task 3 — Tiny UI tweak (Streamlit)

Write `task3_my_ui.py` (you may start by copying `app.py`):

1. Keep chat + `thread_id` in the sidebar.
2. Add **one** visible change of your choice, for example:
   - a sidebar caption reminding students that RAG searches `data/` via Chroma, **or**
   - a second checkbox that prepends "Be extra brief." to the user question before calling the agent.
3. Run it with:

```bash
streamlit run assignment/task3_my_ui.py
```

(from `lecture8/` — keep `from agent import ...` working, or adjust `sys.path` if needed)

---

## Submit

Your `.py` files. Do **not** share your API key, `.env`, or `chroma_db/`.
