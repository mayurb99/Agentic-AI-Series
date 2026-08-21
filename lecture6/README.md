# Lecture 6 — Memory & State (for DevOps Engineers)

This lecture adds **memory** to the same `create_agent` you used in Lecture 5.

**Bridge from L4–L5:**
- Lecture 4 = fixed LCEL chain (`prompt | llm | parser`)
- Lecture 5 = tools + `create_agent` (but every call started fresh — no memory)
- Lecture 6 = same agent, now remembers (short-term thread, summarization, long-term store)

You'll run **3 demos**:

| File | What it teaches |
|---|---|
| `demo_1_short_term_memory.py` | `InMemorySaver` + `thread_id` — same thread remembers; contrast “no memory” |
| `demo_2_summarization_middleware.py` | `SummarizationMiddleware` — compress long chats so the context window doesn’t explode |
| `demo_3_longterm_entity_memory.py` | `InMemoryStore` + `ToolRuntime` — facts that survive a brand-new `thread_id` |

**No RAG / vector-store tools** in this lecture.

---

## 1. Prerequisites

- **Python 3.9 or later**
- A free **Groq API key** — [console.groq.com/keys](https://console.groq.com/keys)
- Lecture 5 completed (you know `@tool` and `create_agent`)

---

## 2. Setup

```bash
cd Agentic-AI-Series/lecture6
python -m venv .venv
```

**Windows (PowerShell):**
```powershell
.\.venv\Scripts\Activate.ps1
```

**macOS / Linux:**
```bash
source .venv/bin/activate
```

```bash
pip install -r requirements.txt
```

**Windows (PowerShell):**
```powershell
Copy-Item demos\.env.example demos\.env
```

**macOS / Linux:**
```bash
cp demos/.env.example demos/.env
```

Put your key in `demos/.env`:
```
GROQ_API_KEY=your_groq_api_key_here
```

---

## 3. Run the demos

From inside `lecture6/`:

```bash
python demos/demo_1_short_term_memory.py
python demos/demo_2_summarization_middleware.py
python demos/demo_3_longterm_entity_memory.py
```

All three use `_client.py` → `get_agent_llm()` (same larger Groq model pattern as Lecture 5 agent demos).

---

## 4. Tiny cheat sheet

| Need | Use |
|---|---|
| Remember turns in **one** chat / ticket | `checkpointer` + same `thread_id` |
| Long chat filling the context window | + `SummarizationMiddleware` |
| Remember facts across **new** chats / days | `store` + remember/recall tools |

`InMemorySaver` / `InMemoryStore` are RAM-only — fine for class; gone when the script exits.
