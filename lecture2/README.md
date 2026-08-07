# Lecture 2 — Embeddings & Vector Databases (for DevOps Engineers)

This lecture turns text into numbers you can search **by meaning** instead of by exact wording, and introduces the vector database (Chroma) that stores and searches them. Everything runs **locally and offline** — `sentence-transformers` for embeddings, `chromadb` for storage and search. No API key is required for demos 1 and 2. Demo 3's short bonus section previews Lecture 3 (RAG) using Groq, but skips gracefully if you don't have a key configured.

You'll run 3 demos:

| File | What it teaches |
|---|---|
| `demo_1_embeddings_basics.py` | What an embedding actually looks like, cosine similarity on real sentence pairs, and why it's the opposite of a hash |
| `demo_2_chroma_persistence.py` | In-memory vs. persistent Chroma, proven by running the script twice in a row |
| `demo_3_semantic_search.py` | The required demo — a 50-document DevOps knowledge base, semantic search vs. naive keyword search, plus a short Groq-powered RAG preview |

---

## 1. Prerequisites

- **Python 3.9 or later** installed. Check with:
  ```bash
  python --version
  ```
- **Internet access for the first run only** — `demo_1` downloads a small (~80 MB) embedding model the first time it runs, then it's cached locally. Every run after that works fully offline.
- *(Optional, for demo 3's bonus section only)* a free **Groq API key** — sign up at [console.groq.com/keys](https://console.groq.com/keys). Demos 1 and 2, and the main part of demo 3, work with no key at all.
- **Git**, to clone this repository.

---

## 2. Clone the repository

```bash
git clone https://github.com/mayurb99/Agentic-AI-Series.git
cd Agentic-AI-Series/lecture2
```

---

## 3. Create and activate a virtual environment

Working inside a virtual environment keeps this course's packages separate from anything else on your machine. Use a **new** virtual environment for this lecture — don't reuse Lecture 1's.

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

This installs `sentence-transformers` and `chromadb` (both new this lecture), plus `groq` and `python-dotenv` carried over from Lecture 1 for demo 3's bonus section only. The first install can take a couple of minutes — `sentence-transformers` pulls in a machine-learning runtime.

---

## 5. (Optional) Add your Groq API key

Only needed if you want to see demo 3's bonus RAG-preview section actually call an LLM. Skip this step entirely if you just want to run the core of all 3 demos.

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

Run each one from inside `lecture2/` (not from inside `demos/`):

```bash
python demos/demo_1_embeddings_basics.py
python demos/demo_2_chroma_persistence.py
python demos/demo_2_chroma_persistence.py
python demos/demo_3_semantic_search.py
```

Notice `demo_2` is listed **twice** — run it back to back on purpose. The first run creates a persistent vector store on disk; the second run finds that data still there and proves it survived the process exiting. Both demo 2 and demo 3 create small `chroma_store_*` folders in this directory the first time they run (already covered by `.gitignore`) — delete them any time to reset a demo back to a first-run state.

Each demo prints its own explanation as it runs — read the console output, not just the final line, since the teaching point in every demo is *the comparison* (semantic vs. keyword search results, in-memory vs. persistent behavior, embeddings vs. hashes), not a single number.

---
