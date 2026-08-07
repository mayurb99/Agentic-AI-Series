# Lecture 2 — Embeddings & Vector Databases (for DevOps Engineers)

This lecture turns text into numbers you can search **by meaning** instead of by exact wording, and introduces the vector database (Chroma) that stores and searches them. Everything runs **locally and offline** — `sentence-transformers` for embeddings, `chromadb` for storage and search. **No API key is required** for any of the three demos.

You'll run 3 demos:

| File | What it teaches |
|---|---|
| `demo_1_embeddings_basics.py` | What an embedding actually looks like, cosine similarity on real sentence pairs, and why it's the opposite of a hash |
| `demo_2_chroma_persistence.py` | In-memory vs. persistent Chroma, proven by running the script twice in a row |
| `demo_3_semantic_search.py` | The required demo — a 50-document DevOps knowledge base, and semantic search vs. naive keyword search |

---

## 1. Prerequisites

- **Python 3.9 or later** installed. Check with:
  ```bash
  python --version
  ```
- **Internet access for the first run only** — `demo_1` downloads a small (~80 MB) embedding model the first time it runs, then it's cached locally. Every run after that works fully offline.
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

This installs `sentence-transformers` and `chromadb` (both new this lecture). The first install can take a couple of minutes — `sentence-transformers` pulls in a machine-learning runtime. No Groq package and no API key are needed for Lecture 2.

---

## 5. Run the demos

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
