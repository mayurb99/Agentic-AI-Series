# Lecture 8 — Live DEMO SCRIPT (Streamlit)

**Setup (once):**
```text
cd lecture8
.\.venv\Scripts\Activate.ps1   # or source .venv/bin/activate
# GROQ_API_KEY already in .env
python ingest.py               # if chroma_db/ missing
streamlit run app.py
```

**UI tips:** Sidebar → **New chat** for a clean thread; turn **Ticket mode** on/off as noted. Memory needs the **same** chat/thread.

---

## Act 1 — Status tool (fake service dict)

| # | Mode | Type this |
|---|------|-----------|
| 1 | Chat | `status of nginx` |
| 2 | Chat | `is redis running?` |

**Expect:** nginx running (~14 days); redis **stopped**.

---

## Act 2 — RAG tool (Chroma runbooks)

| # | Mode | Type this |
|---|------|-----------|
| 3 | Chat | `what does the runbook say if celery is down?` |

**Expect:** broker check / restart steps from celery runbook (not inventing).

---

## Act 3 — Logs tool

| # | Mode | Type this |
|---|------|-----------|
| 4 | Chat | `show me logs of nginx` |
| 5 | Chat | `tail celery-worker.log` |

**Expect:** lines from `data/logs/` (nginx-error / celery-worker.log).

---

## Act 4 — Tool combinations

| # | Mode | Type this |
|---|------|-----------|
| 6 | Chat | `redis is down, what should I do per the runbook?` |
| 7 | Chat | `is celery-worker down? show its logs` |
| 8 | Chat | `nginx issues: check status, runbook, and error logs` |

**Expect:** status + runbook (#6); status + log tail (#7); all three (#8).

---

## Act 5 — Ticket mode (structured IncidentTicket)

1. Sidebar: enable **Ticket mode**
2. Type: `File a ticket for celery-worker`

**Expect:** short ticket summary + JSON (`service_name`, `severity`, `needs_human_approval`, action).

Disable Ticket mode before the memory demo.

---

## Act 6 — Memory (same thread)

Stay in **one** chat (do not click New chat):

| # | Type this |
|---|-----------|
| 9a | `status of nginx` |
| 9b | `what service did we just discuss?` |

**Expect:** follow-up names **nginx** (InMemorySaver + `thread_id`).

---

## Act 7 — Multi-chat tip (sidebar)

1. After Act 6, click **New chat** → ask something about redis.
2. Click the **old** thread in **Your chats** → prior nginx history is still there.
3. Point out: New chat does **not** wipe other chats; each has its own `thread_id`.

---

## One-liner for students

> “Four tools (status / RAG / logs / ticket fill) + short-term memory + multi-thread Streamlit — RAG is just another tool.”
