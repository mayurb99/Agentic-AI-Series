# Lecture 2 — Quick questions

## Q1
What is an embedding, in one sentence?

## Answer
A list of numbers that represents the *meaning* of a piece of text, so similar ideas sit close together in that space (unlike a hash, which is not about meaning).

## Q2
When would semantic search beat simple keyword search?

## Answer
When the query uses different words than the document (paraphrase / synonym) but means the same thing — e.g. “how to restart a failed pod” matching text that says “recover a crashed container.”

## Q3
What is the point of a *persistent* Chroma store vs an in-memory one?

## Answer
Persistent Chroma writes vectors to disk so they survive after the process exits; in-memory is gone when the script ends. Demo 2 proves this by running twice.
