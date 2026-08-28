# Lecture 8 — Mini Project: On-call runbook helper (usecase #1)

L4–L7 were **pieces**. Today we **assemble** them into **one** small product with **real files on disk**.

**What you build:**
- `data/` — real runbooks, logs, and an incident note (students can open these)
- `ingest.py` — load → chunk → embed → persist Chroma (`chroma_db/`)
- `agent.py` — `create_agent` + tools; **RAG is a tool** (`search_runbooks`)
- `app.py` — Streamlit chat UI (multi-chat + optional ticket mode)

**Bridge:**
- L2/L4 = embeddings + Chroma + loaders/splitters (used in `ingest.py`)
- L5 = tools + `create_agent`
- L6 = memory (`thread_id` + checkpointer)
- L7 = structured output (`IncidentTicket`, second call)
- **L8 = one clickable on-call helper**

---

## 1. Prerequisites

- **Python 3.9 or later**
- A free **Groq API key**
- Lectures 5–7 completed (`create_agent`, `thread_id`, structured output familiar)

---

## 2. Setup

```bash
cd Agentic-AI-Series/lecture8
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
Copy-Item .env.example .env
```

**macOS / Linux:**
```bash
cp .env.example .env
```

```
GROQ_API_KEY=your_groq_api_key_here
```

---

## 3. Architecture

```
data/  (runbooks, logs, incidents)
   |
   v
ingest.py  -->  chroma_db/   (gitignored)
   |
   v
agent.py tools:
   - search_runbooks      (RAG over Chroma)
   - check_service_status (fake status dict)
   - tail_log             (safe read of data/logs/)
   |
   v
app.py  (Streamlit)  -->  ChatGroq
```

---

## 4. Run (two steps)

From inside `lecture8/`:

**Step 1 — ingest once** (rebuilds `chroma_db/`):

```bash
python ingest.py
```

**Step 2 — open the UI:**

```bash
streamlit run app.py
```

Open the URL Streamlit prints (usually `http://localhost:8501`).

If you change files under `data/`, run `python ingest.py` again.

---

## 5. Example questions

| Question | Likely tool |
|---|---|
| "Is redis running?" | `check_service_status` |
| "What does the runbook say if celery worker is down?" | `search_runbooks` |
| "Show me logs of nginx" / "Tail celery-worker.log" | `tail_log` (files under `data/logs/` only) |
| "Redis is down — status, runbook steps, and recent celery log" | all three |
| Ticket mode: "File a ticket for celery-worker" | chat tools + structured fill |

---

## 6. Tiny cheat sheet

| Need | Use |
|---|---|
| Build the vector DB | `python ingest.py` |
| Agent brain | `agent.py` |
| Browser UI | `streamlit run app.py` |
| RAG | `search_runbooks` tool (not hardcoded strings) |

**Remember:** shared module first, UI second. Next (L9) we open `create_agent` as a LangGraph `StateGraph`.
