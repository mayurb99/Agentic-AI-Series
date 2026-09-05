# Lecture 11 — Human-in-the-Loop + Persistence

L10's ReAct loop runs until it finishes. Today we **pause for humans** and **survive restarts**.

**Bridge from L10:** Uninterrupted tool loop (`MessagesState` + tools) works.
**Today:** `interrupt_before` / `interrupt` + resume; checkpointers InMemory → Sqlite (Postgres = same API).
**Bridge to L12:** One durable agent with approvals → a **team** under a supervisor.

**Client themes (same family as L9–L10):**
1. **Expense** — draft claim → gate before finance submit
2. **IT + expense** — tool lookups, pause before submit/close
3. **HR leave** — same idea: pause when leave > N days (assignment / PPT examples)

**PPT:** `L11_HITL_Persistence.pptx` (rebuild with `python _build_l11_pptx.py`)

You'll run **3 demos**:

| File | Tools? | What it teaches |
|---|---|---|
| `demo_1_interrupt_before.py` | No | `interrupt_before` + InMemorySaver + resume (expense draft → finance) |
| `demo_2_interrupt_resume.py` | **Yes** | L10 loop + `interrupt()` before submit/close (IT + expense) |
| `demo_3_sqlite_persistence.py` | No | SqliteSaver: pause → “restart” → `Command(resume)` (same claim thread) |

---

## 1. Prerequisites

- Lecture 10 completed (MessagesState + ToolNode + tools_condition)
- Free **Groq API key** for Demo 2 only (Demo 1 and Demo 3 are offline)

## 2. Setup

```bash
cd Agentic-AI-Series/lecture11
python -m venv .venv
```

**Windows (PowerShell):**
```powershell
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
Copy-Item demos\.env.example demos\.env
# Edit demos\.env and set GROQ_API_KEY=...  (needed for Demo 2)
```

**macOS / Linux:**
```bash
source .venv/bin/activate
pip install -r requirements.txt
cp demos/.env.example demos/.env
# Edit demos/.env and set GROQ_API_KEY=...
```

## 3. Run the demos

From `lecture11/`:

```bash
python demos/demo_1_interrupt_before.py
python demos/demo_2_interrupt_resume.py
python demos/demo_3_sqlite_persistence.py
```

## 4. Tiny cheat sheet

| Need | Use |
|---|---|
| Pause **before** a node | `compile(..., interrupt_before=["submit_to_finance"])` |
| Pause **inside** a node | `interrupt(payload)` then `Command(resume=...)` |
| Classroom RAM | `InMemorySaver()` |
| Survive restart | `SqliteSaver` (`langgraph-checkpoint-sqlite`) |
| Multi-worker prod | `PostgresSaver` — **same** `checkpointer=` + `thread_id` API |
| Which pause belongs where | `config = {"configurable": {"thread_id": "expense-claim-101"}}` |

**Why open StateGraph (not only `create_agent`)?** Standard FAQ bots are fine with `create_agent`. Approvals need a **visible** node you can gate — that is why L10 opened the loop and L11 puts a human on it.
