# Lecture 4 — LangChain Intro + Full RAG with LangChain (for DevOps Engineers)

This is the **first LangChain lecture** in the DevOps track. Lecture 3 built a full RAG pipeline by hand in pure Python. This lecture introduces LangChain and LCEL (the `|` pipe operator), surveys **loaders and splitters**, then rebuilds the **entire RAG loop** with LangChain components for every step.

From this lecture onward, chat calls use `langchain` + `langchain-groq` (`ChatGroq`) instead of the raw `groq` SDK client from Lectures 1–3.

You'll run **4 demos**:

| File | What it teaches |
|---|---|
| `demo_1_lcel_basics.py` | The Runnable interface and the `\|` pipe operator |
| `demo_2_batch_stream_async.py` | `.invoke()` vs `.batch()` vs `.stream()` |
| `demo_3_langchain_loaders_splitters.py` | Document + main loaders + main splitters (survey) |
| `demo_4_rag_langchain_e2e.py` | End-to-end RAG with LangChain (load → split → embed/store → retrieve → prompt → LLM → chain) |

---

## 1. Prerequisites

- **Python 3.9 or later** installed. Check with:
  ```bash
  python --version
  ```
- **Internet access for the first run** — Demo 4 downloads a small (~80 MB) embedding model the first time, then it is cached locally.
- A free **Groq API key** — sign up at [console.groq.com/keys](https://console.groq.com/keys). Needed for demos 1, 2, and 4. Demo 3 does **not** need an API key.
- **Git**, to clone this repository.
- Lecture 3's `devops_runbook.pdf` next to this course tree (`../lecture3/devops_runbook.pdf`) — Demo 3 and Demo 4 load it with `PyPDFLoader`.

---

## 2. Clone the repository

```bash
git clone https://github.com/mayurb99/Agentic-AI-Series.git
cd Agentic-AI-Series/lecture4
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

This installs LangChain, ChatGroq, text splitters, Chroma + HuggingFace embeddings wrappers, community loaders, and `pypdf`.

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

Run each one from inside `lecture4/` (not from inside `demos/`):

```bash
python demos/demo_1_lcel_basics.py
python demos/demo_2_batch_stream_async.py
python demos/demo_3_langchain_loaders_splitters.py
python demos/demo_4_rag_langchain_e2e.py
```

`demo_4` creates a small `chroma_store_l4_e2e/` folder in this directory the first time it runs (already covered by `.gitignore`) — delete it any time to reset that demo back to a first-run state.

Each demo prints its own explanation as it runs — read the console output, not just the final answer.
