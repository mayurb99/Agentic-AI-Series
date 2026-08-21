# Lecture 5 — Quick questions

## Q1
What does the `@tool` decorator give the LLM, beyond the Python function itself?

## Answer
A name, a description (from the docstring — used to decide *whether* to call), and a parameter schema (from type hints / Args). That schema is what the model sees.

## Q2
When should you use `bind_tools` vs `create_agent`?

## Answer
- **`bind_tools`** — teach/see the raw step: the model *chooses* a tool; **you** still run it once (manual loop). Good for learning and one-shot demos.  
- **`create_agent`** — the framework runs the multi-step “call tool → feed result → maybe call again” loop for you. Prefer this for real multi-tool / multi-step questions.

## Q3
True or false: After `bind_tools`, the LLM automatically executes your Python function.

## Answer
False. The LLM only returns a tool call (name + args). Your code (or `create_agent`) must invoke the tool and send the result back.
