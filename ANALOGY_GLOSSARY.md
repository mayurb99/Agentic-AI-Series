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
| **A "tool" in the LangChain sense** | A Terraform provider's exposed resource | A Terraform resource exposes a name, typed inputs, and documented behavior — `terraform apply` calls it without reading the provider's source. A LangChain tool is the same shape: name, description, typed arguments. The LLM (and `create_agent`) call it without seeing the function body. |
| **Built-in / community tools (e.g. DuckDuckGo, Wikipedia)** | Vetted community Terraform modules / Ansible Galaxy roles | Prefer a maintained community module over writing a VPC from scratch. Same idea: import a ready-made tool when it fits; write your own with `@tool` when it doesn't. |
| **The `@tool` decorator for custom tools** | Writing your own Ansible module / Terraform provider | When nothing published does your job, wrap your own function behind the same standard interface (name, inputs, behavior) so the orchestrator can call it like any other tool. |
| **`create_agent`** | A Kubernetes scheduler / Ansible playbook runner | In Lecture 1 you branched by hand for one tool call. `create_agent` (LangChain 1.x / LangGraph) is the real loop: declare tools + goal; it decides, calls, observes, and decides again. Prefer this over legacy `AgentExecutor`. |

---

## Seeded in Lecture 6 — Memory & State

| AI concept | DevOps analogy | Why it works |
|---|---|---|
| **Short-term memory (checkpointer + thread_id)** | This ticket's Slack/chat thread | Everything said on ticket #42 stays on ticket #42. A different ticket number is a blank conversation — even with the same agent. |
| **SummarizationMiddleware** | Rolling a long incident log into a short status update | You keep the facts that matter and drop the chatter so the channel (context window) does not fill up. |
| **Long-term / entity store** | A sticky note on a user/service profile | Facts survive a brand-new chat. New thread_id empties short-term memory; the sticky note is still there. |
| **thread_id** | Ticket number / conversation ID | Same ID → load that thread's history. Different ID → start fresh. |

---

## Seeded in Lecture 7 — Structured Output

| AI concept | DevOps analogy | Why it works |
|---|---|---|
| **Structured output / Pydantic schema** | A form with labeled boxes (vs a free-text letter) | Code needs fields (`service_name`, `replicas`), not a paragraph. A form forces named boxes the model must fill. |
| **with_structured_output** | Forcing the model to fill the form via the API | Not "please reply as JSON" hope — the API requires the schema shape (like a mandatory tool call whose args are your fields). |
| **Schema validation** | Request validation on an API endpoint (shape OK ≠ data correct) | Wrong type or forbidden value fails early. A valid payload can still contain wrong facts — same as any API validator. |
| **instructor** | Same form-filling idea using a raw SDK without LangChain | Wrap the raw Groq/OpenAI client and pass `response_model=YourSchema` — portable when that service is not on LangChain. |
| **create_agent response_format** | Agent may use tools, then must finish by filling the form | Same `create_agent` as Lecture 5 — optional tool loop first, then a typed final answer in `result["structured_response"]`. |

---

## Seeded in Lecture 8 — Mini Project (e2e agent + UI)

| AI concept | DevOps analogy | Why it works |
|---|---|---|
| **Assembling L4–L7 into one app** | Wiring services into one runnable stack (compose), not leaving containers unlinked | Tools, memory, and schemas were separate demos — like images with no `docker-compose`. L8 is the compose file: one product classmates can actually use. |
| **Simple chat UI over an agent (Streamlit)** | A basic ops dashboard / chat panel in front of an API | The agent is still the backend. The UI is just request/response + a conversation id — like a thin Grafana/chat front-end over a service you already trust. |
| **Reusable UI shell** | A deployable front-door you keep when the backend changes | Later lectures swap `create_agent` for LangGraph / FastAPI deploy — same chat + `thread_id` shell, new engine behind it. |
| **Light runbook search (tiny RAG without a vector DB)** | `grep` over a small runbook folder before you stand up a full search cluster | Same job as Lecture 4 retrieval (find relevant text, then answer) — intentionally tiny so the product stays beginner-friendly. |

---

## Seeded in Lecture 9 — LangGraph StateGraph Fundamentals

| AI concept | DevOps analogy | Why it works |
|---|---|---|
| **Chain (linear LCEL)** | A fixed CI stage list that always runs A→B→C | No loops, no "if severity high go elsewhere" — predictable pipe. |
| **Graph (`StateGraph`)** | A workflow DAG / runbook with branches and optional loops | Nodes are steps; edges are arrows; conditional edges are `if` routing — same mental model as a deploy pipeline with gates. |
| **State (TypedDict / MessagesState)** | The shared ticket clipboard every step reads/writes | Each node updates fields on one shared object; later nodes see earlier writes. |
| **Node** | One CI job / one runbook step | Takes state in, does work, returns a partial update. |
| **Edge / conditional edge** | Always-next vs. branch on a condition | Fixed edge = always go to B. Conditional = route by severity / tool_calls / approval. |
| **`START` / `END`** | Pipeline entry and exit | Explicit where the workflow begins and finishes. |
| **`compile()` + `invoke` / `stream`** | Build the pipeline once, then run (or watch live) | Compile = assemble the DAG; invoke = one run; stream = watch each step update like `tail -f`. |
| **`create_agent` under the hood** | A managed K8s Deployment vs writing the Pod YAML | L5–L8 used the managed agent; L9 opens the YAML — same graph engine, now you own the nodes. |

---

## Seeded in Lecture 10 — ReAct Agent Loop by Hand

| AI concept | DevOps analogy | Why it works |
|---|---|---|
| **ReAct (Reason → Act → Observe)** | Diagnose → run a command → read output → decide again | Incident loop: think, act with a tool, observe result, loop until done. |
| **`ToolNode`** | The runner that actually executes the chosen Ansible/Terraform action | Model only *requests* a tool call; `ToolNode` runs the function and writes the observation back. |
| **`tools_condition` / route on `tool_calls`** | "Did the playbook ask for another task, or are we done?" | If the last AI message has tool calls → tools node; else → END. |
| **Manual ReAct graph vs `create_agent`** | Hand-written systemd unit vs a managed service | Same loop; L5 hid the wiring; L10 draws every wire so HITL/persistence make sense next. |

---

## Seeded in Lecture 11 — Human-in-the-Loop + Persistence

| AI concept | DevOps analogy | Why it works |
|---|---|---|
| **Human-in-the-loop (HITL) / interrupt** | Change-control gate before prod apply | Graph pauses before a dangerous step; a human must approve; then resume — like a CAB / `terraform apply` confirmation. |
| **`interrupt` / `interrupt_before`** | `kubectl` wait-for-approval / pipeline `manual` gate | Soft pause: state is saved; process can wait or restart and continue from the gate. |
| **Resume (`Command(resume=...)`)** | Clicking "Approve" on the change ticket | Same thread continues from the saved checkpoint with the human's decision. |
| **Checkpointer swap (InMemory → Sqlite → Postgres)** | Temp RAM → local SQLite volume → managed Postgres | Same API (`checkpointer=` + `thread_id`); only the storage backend changes — like swapping a volume driver. |
| **Durable checkpoint across restart** | Job state on disk so a crashed worker can resume | Sqlite file survives process exit; InMemory does not — prove it by restarting. |

---

## Seeded in Lecture 12 — Multi-Agent Supervisor (+ soft Send)

| AI concept | DevOps analogy | Why it works |
|---|---|---|
| **Supervisor agent** | An incident commander / orchestrator service | One brain decides which specialist runs next; workers do not fight over the keyboard. |
| **Worker / specialist subgraph** | A focused microservice or runbook owner | Researcher gathers; writer drafts — each is a reusable component (subgraph), not one mega-prompt. |
| **Routing decision** | Load balancer / queue consumer picking a worker | Supervisor returns "call researcher" or "call writer" or "finish" — like routing a ticket to the right on-call. |
| **`Send()` (light intro)** | Fan-out the same job to N workers (map) | One clear parallel summarize over a few docs — deep map-reduce comes later; today just "dispatch copies." |

---

## Seeded in Lecture 13 — LangSmith Tracing

| AI concept | DevOps analogy | Why it works |
|---|---|---|
| **LangSmith trace / run** | A distributed request with a trace ID (APM) | One user turn is one request; nested LLM/tool steps are spans you open to see latency and errors — same instinct as following a request across services. |
| **Span (LLM or tool)** | One hop in a service mesh / one APM span | A tool call is like an internal HTTP call: you inspect args (request) and return value (response). |
| **LangSmith project** | A dashboard folder / service name for logs | Runs land in a named bucket so class traffic does not mix with prod experiments. |
| **LANGCHAIN_TRACING_V2 + API key** | Feature flag + auth token for the telemetry sidecar | Tracing is off until you flip the flag and provide credentials — like enabling an agent that ships metrics. |

---

## Seeded in Lecture 14 — Datasets, Metrics & Judges

| AI concept | DevOps analogy | Why it works |
|---|---|---|
| **Eval dataset** | Golden fixtures / smoke-test cases in git | Versioned `(input, context, expected)` rows you re-run after every prompt change. |
| **Metric (0–1 score)** | Pass rate / error-budget signal | A single number you can threshold — not a vibes review. |
| **Groundedness / faithfulness** | “Quote the runbook — don’t invent steps” | The answer must stick to provided context; inventing a postgres restart when the runbook never said so is ungrounded. |
| **LLM-as-judge** | Peer review with a written checklist (rubric) | Another reviewer grades 0–1 against explicit rules; useful signal, not infallible gospel. |
| **Prompt A/B** | Canary two configs, keep the better | Same dataset, two system prompts, ship the higher score. |

---

## Seeded in Lecture 15 — CI Eval Gate

| AI concept | DevOps analogy | Why it works |
|---|---|---|
| **CI eval gate** | Required unit-test job that blocks merge | Non-zero exit when average score < threshold — same contract as `pytest` failing the pipeline. |
| **Score threshold policy** | SLO / error-budget thresholds | `ci_min` / warn / page bands mirror how you already escalate when SLOs burn. |
| **Online feedback (thumbs)** | Prod annotations / incident tags that become new test cases | 👎 events get promoted into dataset rows; the gate still must pass before the next deploy. |

---

## Seeded in Lecture 16 — Deploy FastAPI + Docker (Render)

| AI concept | DevOps analogy | Why it works |
|---|---|---|
| **Agent behind FastAPI** | A microservice with `/health` and a POST API | The agent is no longer a script — it is a process you probe, scale, and put behind a URL. |
| **Streaming chat endpoint** | `tail -f` / chunked HTTP responses | Tokens (or chunks) arrive live instead of one blocking response — same “follow the stream” instinct as logs. |
| **Secrets not in the image** | Runtime env / secret store, never bake credentials into a Docker layer | If `GROQ_API_KEY` is in an image layer, it is already leaked; inject at `docker run` or Render Environment Variables. |
| **Render Web Service (class target)** | Managed host for a container with a public URL | Push image or connect repo → set env → get `https://….onrender.com` — Cloud Run is the same idea on GCP (stretch). |

---

*(Future lectures append new rows here, grouped by the lecture that introduced them — e.g. "Seeded in Lecture 17 — MCP".)*
