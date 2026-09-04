# Lecture 10 — ReAct Agent Loop — Built by Hand

L9 taught **graph wiring** (state, nodes, edges). Today we **put tools back** into that graph and rebuild what **`create_agent` hid**: Reason → Act → Observe.

**Bridge from L8 / L5:**
- `create_agent` is a **LangChain API** (`from langchain.agents import create_agent`)
- Under the hood, LangChain 1.x uses **LangGraph** as the engine for the agent loop
- You already shipped a working agent in L8 — today you see the same loop with every wire visible

**Bridge from L9:**
- L9 = draw the flowchart yourself (`StateGraph`, conditional edges) — tools paused on purpose
- L10 = `MessagesState` + `bind_tools` + `ToolNode` + `tools_condition`
- Same idea as L9’s expense router: branch on a condition — today the condition is “did the model request a tool?”

**Bridge to L11:** Once the loop is visible, we add **pauses** (HITL) and **durable checkpoints**.

**When to use what:**
- Standard tool agent (HR FAQ: “How many leave days?”) → `create_agent`
- Need custom gates / HITL / odd branches → open `StateGraph` (this lecture’s loop, then L11+)

**Client themes used in the lecture + demos:**
1. **HR helpdesk** — leave balance lookup (Demo 1 pieces, Demo 3 compare)
2. **IT service desk** — ticket lookup (Demo 2)
3. **Expense policy** — auto vs manager by amount (Demo 2; echoes L9 Demo 2)

**PPT:** `L10_ReAct_By_Hand.pptx` (rebuild with `python _build_l10_pptx.py`)

You'll run **3 demos** (all need Groq):

| File | What it teaches |
|---|---|
| `demo_1_messages_and_toolnode.py` | `MessagesState`, `@tool`, `bind_tools`, one-shot `ToolNode` |
| `demo_2_manual_react_loop.py` | Full ReAct graph with `tools_condition` + stream |
| `demo_3_compare_create_agent.py` | Side-by-side: hand graph vs `create_agent` |

---

## 1. Prerequisites

- **Python 3.9 or later**
- Lectures 5–9 completed (you used `create_agent`; you drew a StateGraph)
- Free **Groq API key** (all three demos)

## 2. Setup

```bash
cd Agentic-AI-Series/lecture10
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

From `lecture10/`:

```bash
python demos/demo_1_messages_and_toolnode.py
python demos/demo_2_manual_react_loop.py
python demos/demo_3_compare_create_agent.py
```

## 4. Tiny cheat sheet

| Piece | Job |
|---|---|
| `MessagesState` | Chat transcript as graph state |
| `llm.bind_tools(tools)` | Model may request tool calls |
| `ToolNode(tools)` | Actually runs the functions |
| `tools_condition` | If tool_calls → tools; else → END |
| Edge `tools → agent` | Observe, then Reason again |

**Remember:** L5–L8 `create_agent` automated this exact loop. L9 taught the wiring. L10 puts tools into that wiring.
