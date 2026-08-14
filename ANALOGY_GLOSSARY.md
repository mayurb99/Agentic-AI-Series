# DevOps → AI Analogy Glossary

**Purpose:** This track teaches Agentic AI to engineers who already know DevOps, not general software engineering. Every AI concept below is anchored to something the student already operates in production. Every lecture in this repo must reuse these exact analogies for these exact concepts — do not invent a new comparison for a concept that's already in this table. New concepts get appended here as new lectures introduce them, so the whole track stays consistent from Lecture 1 to the capstone.

**Rule for instructors/content writers:** if you introduce a new AI concept in a future lecture, add a row here before writing that lecture's slides/transcript, then reuse the wording in both.

---

## Seeded in Lecture 1 — LLM Fundamentals

| AI concept | DevOps analogy | Why it works |
|---|---|---|
| **An LLM API call** | A REST call to a stateless microservice | You send a request, you get a response, the server keeps no memory of you between calls — exactly like calling `POST /predict` on a stateless inference service. Auth is a header (API key), same as any internal service token. |
| **Tokens** | Billed compute units (cloud cost line-items) | You don't get charged per "request," you get charged per unit of work done — like CPU-seconds or GB-processed in a cloud bill. `usage.total_tokens` in an LLM response is that bill, itemized into input (prompt) and output (completion) tokens. |
| **Context window** | A container's memory limit / a fixed-size log buffer | Every container has a memory ceiling — exceed it, and the kernel OOM-kills the process. A ring-buffer log has a fixed capacity — push past it, and the oldest lines silently fall off the front. An LLM's context window behaves like both: exceed it and the call either errors out or the oldest turns get silently dropped. It is never "the model forgot" — it's a hard resource ceiling, like memory or disk. |
| **Temperature** | A chaos-engineering knob | `temperature=0` is a deterministic blue/green rollout — same input, same output, every time, reproducible. `temperature=1` is closer to chaos-monkey — deliberately injecting randomness to explore the space of possible outcomes. You pick the setting based on whether you need reproducibility (ops runbooks, config generation) or creative variety (brainstorming, content drafts). |
| **system / user / assistant roles** | IaC config vs. request payload vs. response body | `system` = the environment defaults baked in at provision time (like a Terraform provider block or a container's baked-in `ENV` vars) — it shapes every request but isn't itself a request. `user` = the actual request payload (like a `kubectl apply` manifest or an API request body). `assistant` = the response body that comes back. Same three-part shape as "config → request → response" you already reason about daily. |
| **Prompt engineering (zero-shot / few-shot / CoT)** | Ad-hoc script vs. reusable module example vs. a step-by-step runbook | **Zero-shot** = writing a one-off shell script with no reference, hoping it works. **Few-shot** = copying a working Terraform module example and adapting it — you give the model 2-3 solved examples before asking your real question. **Chain-of-thought** = a written incident-response runbook that forces step-by-step reasoning ("check logs → check metrics → check recent deploys → conclude") instead of jumping straight to a guess. |

---

## Seeded in Lecture 2 — Embeddings & Vector Databases

| AI concept | DevOps analogy | Why it works |
|---|---|---|
| **Embeddings (semantic vectors)** | A fingerprint of meaning (light contrast with a checksum/hash) | You already know `sha256sum` / Docker digests as fixed-size fingerprints: change one character and the hash flips completely. An embedding is also a fixed-size fingerprint, but built for the **opposite** job — similar *meaning* lands close together as vectors, even when wording barely overlaps. |
| **Vector database (Chroma)** | A special search index — like searching logs by meaning, not exact keywords | Keyword search (`grep` / Ctrl+F) needs the exact words. A vector database is a purpose-built index for one query: "find the K closest meanings." You could store number lists in a normal table; Chroma exists because that one search job is specialized. |
| **In-memory vs. persistent vector store** | Temp container filesystem vs. a mounted volume / saved file on disk | Data written only inside a container vanishes on restart unless you mount a volume. Chroma's in-memory mode is the temp-disk case (fast, gone on exit); `PersistentClient(path=...)` is the mounted-volume case (real files on disk, survives restarts). |
| **Cosine similarity / nearest-neighbour search** | How close two arrows point in the same direction | Picture each embedding as an arrow on a page. Cosine similarity asks whether two arrows point the same way (ignoring length). Near 1.0 ≈ same meaning; near 0 ≈ unrelated. Nearest-neighbour search just scores a query against every stored arrow and keeps the top K. |
| **Local embedding model vs. hosted embedding API** | Running something on your laptop vs. calling a cloud API | `sentence-transformers` downloads once and runs offline on your CPU — free after download, private, you own the model file. A hosted embed endpoint is a normal cloud API call: send text, get numbers back, pay per call, needs network and an API key. |

---

## Seeded in Lecture 3 — RAG From Scratch

| AI concept | DevOps analogy | Why it works |
|---|---|---|
| **Fixed-size chunking** | Cutting a long log file every N lines / characters | You slice the file on a fixed count, even if that cuts mid-sentence. Fast and predictable; some pieces are awkward to read alone. |
| **Sentence-aware chunking** | Cutting at paragraph / sentence boundaries | You wait for a natural break so each piece still makes sense on its own. Chunk sizes vary a little — that is fine. |
| **Hybrid BM25 + dense retrieval** | Keyword search (`grep`) + meaning search (Lecture 2), used together | Keyword search wins on exact error codes and rare terms. Meaning search wins when wording differs but the idea matches. Hybrid gives each method's top 3 picks 3/2/1 points, adds the points, and takes the highest total. |
| **Citations with every RAG answer** | "Show your sources" / link a log line back to its file | Every claim should point back to the chunk it came from — like knowing which log file a line came from. No citation = hard to trust or debug. |

---

## Seeded in Lecture 4 — LangChain Intro + Full RAG with LangChain

| AI concept | DevOps analogy | Why it works |
|---|---|---|
| **LCEL's pipe operator / the Runnable interface** | Unix shell pipes (`cmd1 \| cmd2 \| cmd3`) | `grep "ERROR" app.log \| awk '{print $1}' \| sort` composes small programs into a pipeline. `prompt \| llm \| parser` is the same idea — every piece shares one interface (`Runnable`), so `\|` can connect them. |
| **Batch vs. stream invocation** | One sync REST call vs. a small batch job vs. `tail -f` | `.invoke()` = one request, wait for one response. `.batch()` = hand over several jobs, get all results together. `.stream()` = see output arrive live, like following a log. |
| **Document (`page_content` + `metadata`)** | A log line plus its tags | The text is what you search/read (`page_content`). The tags say where it came from — file, page, service (`metadata`). Loaders and splitters both work in Documents. |
| **Document loader** | `cat` / open the tool that matches the file type | PDF → PDF loader. `.txt` → text loader. CSV → CSV loader. Wrong tool for the format = broken text. You pick the loader that matches the source. |
| **Text splitter / chunker** | How you cut a long log before searching it | Fixed/character cuts are blunt (every N characters). Recursive cuts prefer paragraph/line/space boundaries so pieces stay readable — the everyday default for RAG. |
| **Retriever** | Meaning search that returns the top hits | Like asking Chroma "give me the 3 closest chunks" — a retriever takes a question and returns Documents you can paste into a prompt. |

---

## Seeded in Lecture 5 — Tools & Tool Calling

| AI concept | DevOps analogy | Why it works |
|---|---|---|
| **A "tool" in the LangChain sense** | A Terraform provider's exposed resource | A Terraform resource block exposes a well-defined interface — a name, a set of typed inputs, documented behavior — that `terraform apply` can invoke without knowing a single line of the provider's actual implementation. A LangChain tool is the identical shape: a name, a description, and a typed argument schema, callable by an orchestrator (the LLM, then `create_agent`) with zero visibility into the function body underneath. |
| **Built-in community tools (DuckDuckGo, Wikipedia, calculator)** | Vetted community Terraform modules / Ansible Galaxy roles | You don't hand-write a VPC module from scratch when a well-maintained community Terraform module already does it — you pull the Terraform Registry module or the Ansible Galaxy role instead of reinventing something the community already published and hardened. DuckDuckGo search and Wikipedia lookup are exactly that: ready-to-use, community-maintained tools, zero search-engine or encyclopedia code written by you. |
| **The `@tool` decorator for custom tools** | Writing your own custom Ansible module or Terraform provider | When no existing module does what you need, you don't abandon the standard interface — you write your OWN Ansible module or Terraform provider that exposes the same shape (name, inputs, behavior) so it plugs into the same orchestrator identically to any built-in one. `@tool` does the exact same thing for a plain Python function: wrap it once, and it's callable exactly like DuckDuckGo or Wikipedia. |
| **`create_agent`** | A real orchestration engine — a Kubernetes scheduler, or an Ansible playbook runner | In Lecture 1, tool-calling was entirely manual — you read the model's intent yourself and branched by hand, once, for one step. `create_agent` (LangChain 1.x, built on LangGraph) is the difference between that and a real orchestrator: you declare the available capabilities (tools) and the goal, and the engine decides which capability to invoke next, runs it, observes the result, and decides again — the same relationship a Kubernetes scheduler has to declared pod resource requests, or an Ansible playbook runner has to a declared set of tasks. It replaces the legacy `AgentExecutor` pattern, which is no longer the teaching path from this lecture forward. |

---

*(Future lectures append new rows here, grouped by the lecture that introduced them — e.g. "Seeded in Lecture 6 — ....".)*
