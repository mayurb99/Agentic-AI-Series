# Lecture 1 Assignment — LLM Basics

Small coding practice (~20–30 min). Use Groq like in class. Look at `demos/` for patterns. Do **not** edit the demos — write your own scripts in `lecture1/assignment/`.

**Setup:** finish `lecture1/README.md` (venv, install, API key in `demos/.env`).

```python
import sys
sys.path.insert(0, "../demos")
from _client import DEFAULT_MODEL, get_client
```

---

## Tasks

### Task 1 — Explain an error log

Write `task1_explain_log.py`: one **system** message + one **user** message that asks the model to explain a short error log in plain English. Call Groq once and print the answer.

### Task 2 — Same prompt, two temperatures

In the same script or `task2_temperature.py`: call the model **twice** with the **same** messages — `temperature=0` then `temperature=1`. Print both answers.

### Task 3 — Add one few-shot example

Write `task3_few_shot.py`: before the real question, put **one** example in the `messages` list (see Demo 2). Then ask your real question and print the answer.

---

## Submit

Your `.py` files. Do **not** share your API key or `.env`.
