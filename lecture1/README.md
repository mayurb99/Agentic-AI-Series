# Lecture 1 — LLM Fundamentals (for DevOps Engineers)

This lecture uses the **raw Groq SDK only** — no LangChain, no agent framework, no vector database. The whole point is to feel what it's like to call an LLM with nothing but a plain SDK, the same way you'd `curl` a REST API before reaching for a client library.

You'll run 3 demos:

| File | What it teaches |
|---|---|
| `demo_1_raw_api_basics.py` | Your first raw LLM call, tokens (your bill), temperature, and hitting the context-window limit on purpose |
| `demo_2_prompt_engineering.py` | Zero-shot vs. few-shot vs. chain-of-thought prompting on the same task |
| `demo_3_conversational_loop.py` | Building "memory" by hand — a chatbot has none, you fake it by resending the whole conversation every time |

---

## 1. Prerequisites

- **Python 3.9 or later** installed. Check with:
  ```bash
  python --version
  ```
- A free **Groq API key** — sign up at [console.groq.com/keys](https://console.groq.com/keys). Groq's free tier is enough for every demo in this lecture.
- **Git**, to clone this repository.

---

## 2. Clone the repository

```bash
git clone https://github.com/mayurb99/Agentic-AI-Series.git
cd Agentic-AI-Series/lecture1
```

---

## 3. Create and activate a virtual environment

Working inside a virtual environment keeps this course's packages separate from anything else on your machine.

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

This installs exactly two packages — `groq` (the SDK) and `python-dotenv` (loads your API key from a file). That's it. No LangChain, no ChromaDB — deliberately, for this lecture only.

---

## 5. Add your Groq API key

All 3 demos read their API key from a file called `.env` inside the `demos/` folder. That file is **never committed to Git** (it's listed in `.gitignore`) — you create your own local copy from the provided template:

**Windows (PowerShell):**
```powershell
Copy-Item demos\.env.example demos\.env
```

**macOS / Linux:**
```bash
cp demos/.env.example demos/.env
```

Now open `demos/.env` in any text editor and replace the placeholder with your real key:

```
GROQ_API_KEY=your_groq_api_key_here
```

> **Never share or commit this file once it has your real key in it.** If you accidentally commit a real key, treat it as compromised and generate a new one at [console.groq.com/keys](https://console.groq.com/keys).

---

## 6. Run the demos

Run each one from inside `lecture1/` (not from inside `demos/`):

```bash
python demos/demo_1_raw_api_basics.py
python demos/demo_2_prompt_engineering.py
python demos/demo_3_conversational_loop.py
```

Each demo prints its own explanation as it runs — read the console output, not just the final answer, since the teaching point in every demo is *what happens along the way* (token counts, the model's raw tool-free responses, what gets trimmed from memory, etc.).

---
