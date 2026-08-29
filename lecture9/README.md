# Lecture 9 — LangGraph StateGraph Fundamentals

L8 gave you a **working product** (`create_agent` + UI). Today we **open the gearbox**.

**Bridge from L8:**
- `create_agent` is a **LangChain API** (`from langchain.agents import create_agent`)
- Under the hood, LangChain 1.x uses **LangGraph** as the engine for the agent loop
- **Lecture 9 = draw the graph yourself** — `StateGraph`, state, nodes, edges, `compile()`
- **Tools wait on purpose:** learn wiring first. Tools return in **L10** (`ToolNode` / manual ReAct).

**When to use what:**
- Answer is the product (HR FAQ: “How many leave days?”) → `create_agent`
- Flowchart is the product (leave > 5 days, production access, expense > $500 → manager) → open `StateGraph`

**Client themes used in the lecture + demos:**
1. **HR helpdesk** — FAQ vs leave request with manager gate
2. **IT service desk** — ticket intake pipeline (Demo 1)
3. **Expense approval** — auto vs manager by amount (Demo 2)

**PPT:** `L9_StateGraph_Fundamentals.pptx` (rebuild with `python _build_l9_pptx.py`)

You'll run **3 demos** (Demos 1–2 are pure Python / offline; Demo 3 adds one LLM node):

| File | What it teaches |
|---|---|
| `demo_1_hello_stategraph.py` | IT ticket: intake → classify → prioritize → summarize *(offline)* |
| `demo_2_conditional_routing.py` | Expense: amount ≤ 500 → auto_approve; else → manager_review *(offline)* |
| `demo_3_stream_debug_bridge.py` | HR reply draft via `.stream` + mental map to `create_agent` |

---

## 1. Prerequisites

- **Python 3.9 or later**
- Lectures 5–8 completed (you used `create_agent`)
- Free **Groq API key** for Demo 3 only (Demos 1–2 need no key)

## 2. Setup

```bash
cd Agentic-AI-Series/lecture9
python -m venv .venv
```

**Windows (PowerShell):**
```powershell
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
Copy-Item demos\.env.example demos\.env
# Edit demos\.env and set GROQ_API_KEY=...
```

**macOS / Linux:**
```bash
source .venv/bin/activate
pip install -r requirements.txt
cp demos/.env.example demos/.env
# Edit demos/.env and set GROQ_API_KEY=...
```

## 3. Run the demos

From `lecture9/`:

```bash
# Offline — no API key
python demos/demo_1_hello_stategraph.py
python demos/demo_2_conditional_routing.py

# Needs GROQ_API_KEY in demos/.env
python demos/demo_3_stream_debug_bridge.py
```

## 4. Tiny cheat sheet

| Need | Use |
|---|---|
| Shared clipboard | `TypedDict` state |
| One step | `builder.add_node("name", fn)` |
| Always next | `builder.add_edge("a", "b")` |
| Branch | `builder.add_conditional_edges("a", router_fn)` |
| Run | `graph = builder.compile()` then `.invoke` / `.stream` |

**Remember:** `create_agent` already compiled a graph for you. Today you own the nodes. Tools return in Lecture 10.
