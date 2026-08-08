# Lecture 3 — RAG From Scratch (for DevOps Engineers)

This is the **last "zero LangChain" lecture** in the DevOps track. Everything here is plain Python: the raw Groq SDK, `sentence-transformers`, `chromadb`, plus two new libraries — `pypdf` (PDF text) and `rank-bm25` (keyword ranking). You build a full RAG pipeline by hand once, so Lecture 4's LangChain rebuild feels like relief instead of magic.

You'll run **3 demos**:

| File | What it teaches |
|---|---|
| `demo_1_chunking_strategies.py` | Fixed-size vs. sentence-aware chunking |
| `demo_2_hybrid_retrieval.py` | Keyword search (BM25) + meaning search (embeddings) used together |
| `demo_3_rag_pipeline_pdf.py` | Full RAG on a PDF: load → chunk → store → retrieve → prompt → answer with citations |

**The loop you should leave knowing:** chunk → embed → search → stuff into prompt → answer with sources.

---

## 1. Prerequisites

- **Python 3.9 or later**
- **Internet for the first run only** — demos 2 and 3 download the same small (~80 MB) embedding model from Lecture 2, then it is cached
- A free **Groq API key** from [console.groq.com/keys](https://console.groq.com/keys) — needed for demo 3 only (demos 1 and 2 need no key)
- **Git**, to clone this repository

---

## 2. Clone the repository

```bash
git clone https://github.com/mayurb99/Agentic-AI-Series.git
cd Agentic-AI-Series/lecture3
```

---

## 3. Create and activate a virtual environment

Use a **new** virtual environment for this lecture.

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

---

## 4. Install dependencies

```bash
pip install -r requirements.txt
```

---

## 5. Add your Groq API key

Needed for **demo 3 only**. Demos 1 and 2 never call an LLM.

**Windows (PowerShell):**
```powershell
Copy-Item demos\.env.example demos\.env
```

**macOS / Linux:**
```bash
cp demos/.env.example demos/.env
```

Open `demos/.env` and set:

```
GROQ_API_KEY=your_groq_api_key_here
```

> **Never share or commit this file once it has your real key.** It is already in `.gitignore`.

---

## 6. Run the demos

Run each one from inside `lecture3/` (not from inside `demos/`):

```bash
python demos/demo_1_chunking_strategies.py
python demos/demo_2_hybrid_retrieval.py
python demos/demo_3_rag_pipeline_pdf.py
```

Demo 3 reads `devops_runbook.pdf` in this folder (same platform runbook content demos 1–2 use as Python data). First run of demo 3 also creates `chroma_store_demo3/` (gitignored) — delete that folder anytime to reset storage.

Each demo prints its own explanation. Read the console output; the teaching point is the comparison, not a single number.
