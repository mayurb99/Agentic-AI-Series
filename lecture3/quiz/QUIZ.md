# Lecture 3 — Quick questions

## Q1
Why do we chunk documents before embedding them for RAG?

## Answer
So each piece fits retrieval and the context window, and search can return the *relevant* passage instead of a whole long PDF. Fixed-size vs sentence-aware are two ways to split.

## Q2
What is hybrid retrieval (as in this lecture)?

## Answer
Combining keyword ranking (BM25) with meaning search (embeddings) so you catch both exact terms and paraphrases.

## Q3
In a RAG answer, why ask the model to include citations / sources?

## Answer
So the user can check which chunk or page the claim came from — answers should be grounded in retrieved text, not invented.
