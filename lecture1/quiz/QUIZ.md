# Lecture 1 — Quick questions

## Q1
What does `temperature=0` usually mean for an LLM call?

## Answer
Low / near-zero randomness — the model tends to give the same answer for the same prompt. Higher temperature (e.g. 1) adds more variety.

## Q2
Name the three common message roles you pass in a chat API, and what each is for.

## Answer
- **system** — instructions / persona for the model  
- **user** — the human’s question or input  
- **assistant** — the model’s previous replies (used when you build conversation “memory” by hand)

## Q3
Why do demos print `prompt_tokens` / `completion_tokens` / `total_tokens`?

## Answer
Tokens are the unit you are billed for (and that fill the context window). Prompt tokens = what you send; completion tokens = what the model writes back.
