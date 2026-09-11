# Lecture 12 — Multi-Agent Supervisor (+ soft Send)

**Team day.** One agent becomes a **team**: supervisor routes to specialists.

**Bridge from L11:** Durable single agent with approvals.
**Today:** supervisor + researcher/writer workers; light `Send()` fan-out (not deep map-reduce).
**Bridge to L13:** It works in class — next we **see** traces in LangSmith.

You'll run **2 demos**:

| File | What it teaches |
|---|---|
| `demo_1_supervisor_routing.py` | Supervisor picks researcher / writer / FINISH |
| `demo_2_soft_send_fanout.py` | Light `Send()` parallel summarize over a few docs |

---

## 1. Prerequisites

- Lectures 9–11; Groq API key

## 2. Setup

```bash
cd Agentic-AI-Series/lecture12
python -m venv .venv
# activate
pip install -r requirements.txt
# Copy demos/.env.example → demos/.env
```

## 3. Run

```bash
python demos/demo_1_supervisor_routing.py
python demos/demo_2_soft_send_fanout.py
```

## 4. Cheat sheet

| Role | Job |
|---|---|
| Supervisor | Incident commander — choose next worker or finish |
| Worker | Specialist node (research OR write) |
| `Send()` | Fan-out the same work to N copies (soft intro) |

**Soft cliff:** deep map-reduce / long-doc patterns come in later phases — today one clear fan-out is enough.
