# Lecture 2 Assignment — Embeddings Basics

Small coding practice (~20–30 min). No API key. Use `sentence-transformers` and `chromadb` like class. Look at `demos/` for patterns. Do **not** edit the demos — write your own scripts in `lecture2/assignment/`.

**Setup:** finish `lecture2/README.md` (new venv + `pip install`). Run from `lecture2/`.

---

## Tasks

### Task 1 — Cosine similarity for 3 sentences

Write `task1_similarity.py`: pick **3 short sentences**, embed them with `all-MiniLM-L6-v2`, print cosine similarity for **1 vs 2** and **1 vs 3**. (Demo 1 uses `cos_sim`.)

### Task 2 — Tiny Chroma search

Write `task2_chroma_search.py`: put **5 short docs** in Chroma (in-memory `chromadb.Client()` is fine), query with **one** sentence, print the **top match**. (See Demo 2 / Demo 3 for `add` / `query`.)

### Task 3 — Change the query

In the same script or `task3_new_query.py`: change the query text and print the **new** top match.

---

## Submit

Your `.py` files. You do **not** need to submit any `chroma_store_*` folders.
