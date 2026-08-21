# Lecture 4 — Quick questions

## Q1
What does LCEL’s `|` (pipe) give you, in plain terms?

## Answer
A way to chain Runnables with the same interface — e.g. `prompt | llm | parser` — like a Unix shell pipe, instead of calling each step by hand.

## Q2
When would you use `.stream()` instead of `.invoke()` on a chain?

## Answer
When you want tokens (or chunks) to arrive as they are generated — better for live UIs / demos. `.invoke()` waits for the full result; `.batch()` runs many inputs together.

## Q3
In LangChain RAG, what do loaders and splitters do?

## Answer
**Loaders** turn files (e.g. PDF via `PyPDFLoader`) into Documents. **Splitters** break those Documents into smaller chunks before embedding and storing in a vector store.
