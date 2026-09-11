# Lecture 8 — Resume & Interview Notes

Use this after you finish the on-call mini-project (`ingest.py` → `agent.py` → `streamlit run app.py`). Keep wording honest: classroom demo, not production SRE tooling.

---

## Interview speaking points

**What I built.** I built a small on-call runbook helper: an agent that can check fake service status, search runbooks with RAG, and tail classroom log files, then answer in a Streamlit chat UI. Optional ticket mode fills a structured incident ticket after the tool-using chat step.

**Stack.** Python, LangChain `create_agent`, Groq (`ChatGroq`), Chroma + HuggingFace embeddings for RAG, LangGraph in-memory checkpointer with `thread_id` for chat memory, Pydantic for the ticket schema, and Streamlit for a multi-chat UI.

**Problem it solves.** On-call questions usually need several sources at once (status + runbook + recent logs). I exposed those as tools so the model chooses what to call instead of hardcoding answers, and I kept RAG behind `search_runbooks` so retrieval is explicit.

**If asked “tell me about a project.”** “I shipped an end-to-end agentic mini-app: ingest docs into Chroma, wrap status/RAG/log helpers as tools, add thread memory, and put a multi-chat Streamlit front end on top—with a ticket path that uses structured output. It’s a teaching project, but the shape matches how I’d wire a real on-call assistant: tools first, UI second, no invented metrics.”

---

## Resume bullets (use only these four)

- Built an on-call runbook helper that combines service-status checks, Chroma RAG over runbooks, and safe log tailing as LangChain tools behind a Groq-powered agent.
- Implemented document ingest (load → chunk → embed → persist) into a local Chroma collection so runbook search is retrieval-backed, not hardcoded text.
- Added Streamlit multi-chat UI with per-thread memory (`thread_id` + checkpointer) so users can open parallel conversations without wiping prior threads.
- Delivered optional ticket mode that gathers tool context in chat, then fills a Pydantic `IncidentTicket` (severity, status summary, recommended action) via structured output.
