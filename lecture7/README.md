# Lecture 7 — Structured Output (for DevOps Engineers)

This lecture teaches how to get **typed objects** (forms) from an LLM — not free-text paragraphs.

**Bridge from L4–L6:**
- Lecture 4 = fixed chains
- Lecture 5 = tools + `create_agent` (answers were free text)
- Lecture 6 = same agent, now remembers
- Lecture 7 = answers as Pydantic objects you can code against

You'll run **3 demos**:

| File | What it teaches |
|---|---|
| `demo_1_structured_output_basics.py` | JSON vs dict vs Pydantic; old parser vs `with_structured_output`; tiny `create_agent(..., response_format=)` |
| `demo_2_instructor_framework_agnostic.py` | Same idea with `instructor` + raw Groq SDK (no LangChain) |
| `demo_3_retry_and_validation.py` | `@field_validator` + manual LangChain retry + instructor `max_retries` + `.with_retry` |

---

## 1. Prerequisites

- **Python 3.9 or later**
- A free **Groq API key**
- Lectures 5–6 completed (`create_agent` familiar)

---

## 2. Setup

```bash
cd Agentic-AI-Series/lecture7
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

```
GROQ_API_KEY=your_groq_api_key_here
```

---

## 3. Run the demos

From inside `lecture7/`:

```bash
python demos/demo_1_structured_output_basics.py
python demos/demo_2_instructor_framework_agnostic.py
python demos/demo_3_retry_and_validation.py
```

---

## 4. Tiny cheat sheet

| Need | Use |
|---|---|
| Stay in LangChain, one call fills a schema | `llm.with_structured_output(Schema)` |
| Raw Groq SDK / no LangChain | `instructor` + `response_model=` |
| Agent may use tools, then finish typed | `create_agent(..., response_format=Schema)` |
| Extra business rules | `@field_validator` + retry |

**Remember:** valid shape ≠ true facts. Schema checks structure, not truth.
