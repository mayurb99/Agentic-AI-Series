# Lecture 5 — Tools & Tool Calling (for DevOps Engineers)

This lecture introduces **tools** — a normal Python function wrapped so an LLM can decide to call it with real arguments. You'll write custom tools with `@tool`, reuse built-in community tools, then wire them into `create_agent` (LangChain 1.x / LangGraph) — the modern replacement for the legacy `AgentExecutor` pattern, which this course does not teach.

**Same 3-demo teaching arc as MLOps Lecture 6**, but DevOps-flavored and **no RAG / vector-store / knowledge-base tools**.

You'll run **3 demos**:

| File | What it teaches |
|---|---|
| `demo_1_custom_tools.py` | Custom `@tool` tools (datetime, days-between, service status). Print schemas, then `bind_tools` + a one-shot manual tool loop |
| `demo_2_builtin_tools_agent.py` | Built-in tools (Wikipedia / DuckDuckGo) + tiny calculator, wired with `create_agent`. Network calls are try/except so class keeps moving if search flakes |
| `demo_3_devops_agent.py` | `create_agent` with 3 simple custom DevOps tools (status, runbook dict, threshold). Multi-step questions; watch tools fire in sequence |

---

## 1. Prerequisites

- **Python 3.9 or later** installed. Check with:
  ```bash
  python --version
  ```
- A free **Groq API key** — sign up at [console.groq.com/keys](https://console.groq.com/keys). Needed for all three demos.
- **Git**, to clone this repository.

---

## 2. Clone the repository

```bash
git clone https://github.com/mayurb99/Agentic-AI-Series.git
cd Agentic-AI-Series/lecture5
```

---

## 3. Create and activate a virtual environment

Use a **new** virtual environment for this lecture — don't reuse a previous one.

**Windows (PowerShell):**
```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

**macOS / Linux:**
```bash
python -m venv .venv
source .venv/bin/activate
```

You'll know it worked because your terminal prompt now starts with `(.venv)`.

---

## 4. Install dependencies

```bash
pip install -r requirements.txt
```

This installs `langchain`, `langchain-groq`, `langchain-community`, `python-dotenv`, plus Wikipedia / DuckDuckGo packages for Demo 2. `create_agent` comes from the same `langchain` package. There is **no** Chroma / RAG dependency in this lecture.

---

## 5. Add your Groq API key

**Windows (PowerShell):**
```powershell
Copy-Item demos\.env.example demos\.env
```

**macOS / Linux:**
```bash
cp demos/.env.example demos/.env
```

Then open `demos/.env` and replace the placeholder with your real key:

```
GROQ_API_KEY=your_groq_api_key_here
```

> **Never share or commit this file once it has your real key in it.** It's already listed in `.gitignore`. If you accidentally commit a real key, treat it as compromised and generate a new one at [console.groq.com/keys](https://console.groq.com/keys).

---

## 6. Run the demos

Run each one from inside `lecture5/` (not from inside `demos/`):

```bash
python demos/demo_1_custom_tools.py
python demos/demo_2_builtin_tools_agent.py
python demos/demo_3_devops_agent.py
```

**A note on the model:** Demo 1 uses `_client.py`'s `get_llm()` (small model, one-shot `bind_tools`). Demos 2 and 3 use `get_agent_llm()` — a larger model. `create_agent`'s multi-step loop needs a model that reliably stops calling tools when it already has enough information.

**A note on network:** Demo 2 uses live Wikipedia (and optionally DuckDuckGo). If search fails in class, the demo still prints the tool wiring and a clear error message — that is intentional.

Each demo prints numbered steps as it runs. In Demos 2 and 3, read the console for **which tool was chosen and with what arguments** — that is the teaching point, not only the final answer.

---
