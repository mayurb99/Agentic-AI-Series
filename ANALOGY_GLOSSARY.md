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
| **Embeddings (semantic vectors)** | The opposite of a checksum/hash | You already know `sha256sum` and Docker image digests: change one byte of input, and the hash changes completely (the "avalanche effect") — hashes are built to *destroy* similarity. An embedding is built to do the **opposite**: two sentences with similar *meaning* land close together as vectors, even if barely a single word overlaps. Same "turn data into a fixed-size fingerprint" idea, opposite goal. |
| **Vector database (Chroma)** | A purpose-built index, like Prometheus for metrics or Elasticsearch for text | You could technically store metrics in Postgres, but you use Prometheus because it's built for one query pattern (time-range aggregation) and is dramatically faster at it. A vector database is the same trade: you could store embeddings as arrays in Postgres, but Chroma is purpose-built for one query pattern — "find the K closest vectors" — and is dramatically faster at exactly that. |
| **In-memory vs. persistent vector store** | An ephemeral container filesystem vs. a mounted volume | Data in a container's own filesystem vanishes the moment the container restarts, unless you mount a volume. Chroma's in-memory mode is the container-filesystem case (fast, gone on restart); `persist_directory` is the mounted-volume case (survives restarts, backed by real files on disk). |
| **Cosine similarity / nearest-neighbour search** | Fuzzy anomaly detection against a baseline | Think of an anomaly-detection system comparing a new metrics vector (CPU, latency, error rate) against historical "normal" vectors to find the closest match, regardless of absolute scale. Cosine similarity does the same thing to text: it compares the *direction* two vectors point, ignoring their magnitude, to score how alike two pieces of text are in meaning. |
| **Local embedding model vs. hosted embedding API** | Self-hosted service vs. managed SaaS | Running `sentence-transformers` locally is like self-hosting your own Elasticsearch cluster — free, private, no network call, but you own the compute and the model version. A hosted embedding API is the managed-SaaS trade-off: pay per call, zero ops, but a network dependency and a per-token bill, same as choosing a managed database over running your own. |

---

## Seeded in Lecture 3 — RAG From Scratch + Advanced Retrieval

| AI concept | DevOps analogy | Why it works |
|---|---|---|
| **Fixed-size vs. sentence-aware chunking** | Size-based vs. time-based log rotation | Fixed-size chunking rotates every N characters no matter what's on the line where the cut falls — like rotating a log every N megabytes, mid-write, regardless of content. Sentence-aware chunking rotates only at a natural boundary — like time-based log rotation, which always waits for midnight rather than slicing a line in half. |
| **HyDE (hypothetical document embeddings)** | Synthetic monitoring / a canary request | You don't have the real answer yet, so you generate a plausible synthetic one first, purely to probe the system before doing the real lookup — exactly like synthetic monitoring fires a fabricated but realistic request to test a system before real traffic arrives. The synthetic document, like a canary request, is never shown to a real user. |
| **Hybrid BM25 + dense retrieval** | A signature-based WAF rule + an ML-based anomaly detector | BM25 (sparse/keyword) is a signature-based WAF rule — exact/keyword match, unbeatable when the pattern is present, blind the instant it isn't. Dense retrieval (embeddings) is an ML-based anomaly detector — fuzzy, semantic, robust to rewording. Real defenses run both, combined, because two independent signals beat either one alone — hybrid retrieval is the identical idea, applied to search instead of security. |
| **Parent-child / small-to-big chunking** | A Grafana dashboard drilling from an aggregated metric into the full raw trace | You search on a small, precise chunk (the aggregated metric a dashboard panel shows), but what you actually need for context is the full underlying detail (the raw trace behind that panel). Parent-child chunking does the identical thing to text: search over small, precise child chunks, but return the full parent chunk they belong to as the context an LLM actually reads. |
| **Citations with every RAG answer** | Structured logging with a request ID / audit trail | Every response must be traceable back to its source, the same way every log line should be traceable to a specific request ID or commit hash. An answer with no citation is like a log line with no request ID — impossible to verify, impossible to debug when it's wrong. (Automated evaluation of citation quality — RAGAS-style metrics — is a later phase's topic; this lecture only builds the citation mechanic itself.) |

---

## Seeded in Lecture 4 — LangChain Intro + LCEL

| AI concept | DevOps analogy | Why it works |
|---|---|---|
| **LCEL's pipe operator / the Runnable interface** | Unix shell pipes (`cmd1 \| cmd2 \| cmd3`) | `grep "ERROR" app.log \| awk '{print $1}' \| sort \| uniq -c` composes small, single-purpose programs into a pipeline, each one's output feeding the next one's input. `prompt \| llm \| parser` is the identical idea — every piece (a prompt template, a chat model, an output parser, even your own plain function) shares one interface (`Runnable`), so `\|` can connect any of them the same way a shell pipe connects any two programs that read stdin and write stdout. |
| **Batch vs. stream vs. async invocation** | A synchronous REST call vs. a batch ETL job vs. `tail -f` on a live log | `.invoke()` is a synchronous REST call — one request, block until the one response comes back. `.batch()` is a batch ETL job — hand over a whole list of work up front, get every result back once the batch finishes, running concurrently instead of one at a time. `.stream()` is `tail -f` on a live log file — output arrives incrementally, in real time, instead of you waiting silently for the whole thing and reading it all at once. `.ainvoke()`/`.astream()` are the async twins of the first and third, for use inside an application that can't afford to block its event loop while waiting. |
| **Callback-based token streaming to a web client** | CI/CD webhook callbacks / Server-Sent Events | A callback handler is a webhook: instead of polling a pipeline asking "are you done yet?", the pipeline calls YOUR code back the instant something happens — a Slack alert on each build stage completing, not one message at the very end. Server-Sent Events do the identical thing over HTTP: the server pushes each new piece of data to the client as it becomes available, instead of the client waiting silently for one final response. |

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
