# Lecture 12 Assignment — Supervisor Team

Small coding practice (~25–40 min). Soft density — supervisor first. Do **not** edit the demos.

**Setup:** finish `lecture12/README.md`.

```python
import sys
sys.path.insert(0, "../demos")
from _client import get_llm
```

---

## Tasks

### Task 1 — Two-worker supervisor

Write `task1_supervisor.py`: supervisor routes between `lookup` and `summarize` (your own short node bodies — fake data OK for lookup). Workers return to supervisor. End when supervisor chooses FINISH. Print an audit list.

### Task 2 — Swap the incident

Write `task2_rerun.py`: reuse Task 1 (import or copy) and run **two** different incident strings. Show both Slack-style outputs.

### Task 3 — Soft Send (optional)

Write `task3_send.py`: fan-out with `Send` over a list of 2–3 short strings; gather summaries with `Annotated[list, operator.add]`. Keep it smaller than Demo 2.

---

## Submit

Your `.py` files. Do **not** share `.env`.
