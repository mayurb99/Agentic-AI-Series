# Lecture 11 Assignment — HITL + Persistence

Small coding practice (~25–40 min). Look at `demos/`. Do **not** edit the demos — write scripts in `lecture11/assignment/`.

**Setup:** finish `lecture11/README.md`.

```python
import sys
sys.path.insert(0, "../demos")
from _client import get_llm  # only if you need an LLM / tools node
```

**Themes:** keep HR / IT / expense (same as L9–L11). No DevOps / terraform stories required.

---

## Tasks

### Task 1 — `interrupt_before` expense gate

Write `task1_interrupt_before.py`:

- Nodes: `draft_claim` → `submit_to_finance`
- Compile with `InMemorySaver` and `interrupt_before=["submit_to_finance"]`
- Invoke a sample claim (e.g. employee + amount), print `get_state(...).next`
- Resume with `invoke(None, config)`
- Prove `submit_to_finance` only runs after resume (`submitted` stays False while paused)

### Task 2 — Tools optional + `interrupt` + `Command(resume=...)`

Write `task2_interrupt_command.py`:

**Minimum (required):** an `approval` node that calls `interrupt({"action": ...})`. Resume once with `"approve"` and once with `"reject"` (two `thread_id`s). Print different outcomes.

**Stretch (optional, shows L10 connectivity):** add one tiny `@tool` (e.g. `leave_balance` or `lookup_ticket`) + `MessagesState` agent hop **before** the approval node. Gate before a `submit` / `close` step.

### Task 3 — Sqlite pause (optional)

Write `task3_sqlite_pause.py`: copy the Demo 3 idea — pause an expense/IT claim to `assignment/my_checkpoints.sqlite`, close the connection, reopen with the **same** `thread_id`, resume with `Command(resume=...)`. Print notes before/after restart.

---

## Submit

Your `.py` files (and sqlite file only if asked). Never share API keys.
