# Lecture 4 Assignment — LCEL, Splitters, RAG

Small coding practice (~20–30 min). Use LangChain like in class. Look at `demos/` for patterns. Do **not** edit the demos — write your own scripts in `lecture4/assignment/`.

**Setup:** finish `lecture4/README.md` (venv, install, API key in `demos/.env`).

```python
import sys
sys.path.insert(0, "../demos")
from _client import get_llm
```

---

## Tasks

### Task 1 — Tiny LCEL chain

Write `task1_lcel.py`: build `ChatPromptTemplate | llm | StrOutputParser` (see Demo 1). Ask **one** DevOps question with `.invoke()`. Print the answer.

### Task 2 — Split one paragraph

Write `task2_splitter.py`: take **one short paragraph** of your own text. Split it with `RecursiveCharacterTextSplitter` (`chunk_size=70`, `chunk_overlap=0`). Print how many chunks you got. (Demo 3 shows this.)

### Task 3 — One small RAG change (optional)

Copy `demos/demo_4_rag_langchain_e2e.py` into `assignment/` (keep PDF paths working). Do **one** of these: change the questions list to **one new question**, **or** add **one** extra `Document` and ask about it. Run your copy.

---

## Submit

Your `.py` files. Do **not** share your API key or `.env`.
