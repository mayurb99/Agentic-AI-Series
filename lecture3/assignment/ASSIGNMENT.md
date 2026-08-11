# Lecture 3 Assignment — RAG Basics

Small coding practice (~20–30 min). Same tools as class. Look at `demos/` for patterns. Do **not** edit the original demos — use copies or new scripts in `lecture3/assignment/`.

**Setup:** finish `lecture3/README.md` (venv, install, API key in `demos/.env` for Task 2).

```python
import sys
sys.path.insert(0, "../demos")
from _chunking import fixed_size_chunks, sentence_aware_chunks
```

---

## Tasks

### Task 1 — Two kinds of chunks

Write `task1_chunking.py`: take **one paragraph** of your own text. Print **fixed-size** chunks and **sentence-aware** chunks. Reuse or copy the helpers from `demos/_chunking.py`.

### Task 2 — One new RAG question

Copy `demos/demo_3_rag_pipeline_pdf.py` into `assignment/` (keep PDF paths working). Change the `questions` list to **one new question you write** about the runbook. Run your copy — this is a code edit, not paste-the-output notes.

### Task 3 — Keyword vs meaning (tiny)

Write `task3_keyword_vs_meaning.py`: a **small list** of short strings (include at least one new string of yours). For **one** query, print the top keyword hit and the top meaning (embedding) hit. Keep it tiny. Demo 2 shows the idea.

---

## Submit

Your `.py` files. Do **not** share your API key or `.env`.
