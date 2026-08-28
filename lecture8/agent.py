# agent.py
# Lecture 8 — On-call runbook helper (usecase #1)
#
# Tools (RAG is ONE of them):
#   1) search_runbooks      — Chroma similarity search over data/ (after ingest.py)
#   2) check_service_status — fake status dict
#   3) tail_log             — last N lines from data/logs/
#   4) optional ticket fill — chat+tools first, then structured IncidentTicket
#
# Used by: app.py
# Setup:   python ingest.py   then   streamlit run app.py

from __future__ import annotations

import os
from pathlib import Path
from typing import Literal, Optional

from dotenv import load_dotenv
from langchain.agents import create_agent
from langchain_chroma import Chroma
from langchain_core.tools import tool
from langchain_groq import ChatGroq
from langchain_huggingface import HuggingFaceEmbeddings
from langgraph.checkpoint.memory import InMemorySaver
from pydantic import BaseModel, Field

# Load GROQ_API_KEY from lecture8/.env
HERE = Path(__file__).resolve().parent
load_dotenv(HERE / ".env")
load_dotenv()

GROQ_API_KEY = os.getenv("GROQ_API_KEY")
AGENT_MODEL = "openai/gpt-oss-120b"
CHROMA_DIR = HERE / "chroma_db"
COLLECTION_NAME = "oncall_runbooks"
EMBED_MODEL = "sentence-transformers/all-MiniLM-L6-v2"
LOGS_DIR = HERE / "data" / "logs"

# Fake classroom status (stand-in for a real status API)
SERVICES = {
    "nginx": {"status": "running", "uptime": "14 days"},
    "redis": {"status": "stopped", "uptime": None},
    "celery-worker": {"status": "stopped", "uptime": None},
    "postgres": {"status": "running", "uptime": "30 days"},
}

_vectorstore = None


def get_llm(temperature: float = 0) -> ChatGroq:
    if not GROQ_API_KEY:
        raise RuntimeError(
            "GROQ_API_KEY not found.\n"
            "Copy .env.example to .env and fill in your key\n"
            "from https://console.groq.com/keys"
        )
    return ChatGroq(
        model=AGENT_MODEL,
        api_key=GROQ_API_KEY,
        temperature=temperature,
        max_tokens=800,
    )


def get_vectorstore() -> Chroma:
    """Open the Chroma DB built by ingest.py. Clear error if missing."""
    global _vectorstore
    if _vectorstore is not None:
        return _vectorstore

    if not CHROMA_DIR.exists():
        raise RuntimeError(
            "Chroma DB not found.\n"
            "Run this first from lecture8/:\n"
            "  python ingest.py"
        )

    embeddings = HuggingFaceEmbeddings(model_name=EMBED_MODEL)
    _vectorstore = Chroma(
        persist_directory=str(CHROMA_DIR),
        embedding_function=embeddings,
        collection_name=COLLECTION_NAME,
    )
    return _vectorstore


# =============================================================================
# L7 schema — incident ticket (structured finish)
# =============================================================================
class IncidentTicket(BaseModel):
    """Typed incident ticket the agent fills when asked to file a ticket."""

    title: str = Field(description="Short incident title")
    service_name: str = Field(description="Affected service name")
    severity: Literal["low", "medium", "high", "critical"] = Field(
        description="Severity: low, medium, high, or critical"
    )
    status_summary: str = Field(
        description="One sentence: current status of the service"
    )
    recommended_action: str = Field(
        description="One or two sentences: what on-call should do next"
    )
    needs_human_approval: bool = Field(
        description="True if a human must approve before action"
    )


# =============================================================================
# Tools
# =============================================================================
@tool
def check_service_status(service_name: str) -> str:
    """
    Check whether a service is running.
    Use when the user asks if a service is up, down, or healthy.
    Supported: nginx, redis, celery-worker, postgres.
    """
    name = service_name.lower().strip()
    if name not in SERVICES:
        return (
            f"Unknown service '{name}'. "
            "Try: nginx, redis, celery-worker, postgres."
        )
    info = SERVICES[name]
    if info["status"] == "running":
        return f"Service '{name}' is RUNNING. Uptime: {info['uptime']}."
    return f"Service '{name}' is STOPPED."


@tool
def search_runbooks(query: str, k: int = 3) -> str:
    """
    RAG search over runbooks / logs / incident notes in data/ (via Chroma).
    Use when the user asks what to do, how to fix something, or for runbook steps.
    """
    q = (query or "").strip()
    if not q:
        return "Please provide a search query (e.g. redis down, nginx 502)."

    try:
        vs = get_vectorstore()
    except RuntimeError as exc:
        return str(exc)

    docs = vs.similarity_search(q, k=max(1, min(k, 5)))
    if not docs:
        return f"No runbook hits for '{query}'."

    lines = []
    for i, doc in enumerate(docs, 1):
        source = doc.metadata.get("source", "unknown")
        text = doc.page_content.strip().replace("\n", " ")
        if len(text) > 400:
            text = text[:400] + "..."
        lines.append(f"[{i}] source={source}\n{text}")
    return "Runbook hits:\n\n" + "\n\n".join(lines)


# Friendly aliases so "nginx" / "celery" resolve to real filenames under data/logs/
_LOG_ALIASES = {
    "nginx": "nginx-error.log",
    "nginx-error": "nginx-error.log",
    "celery": "celery-worker.log",
    "celery-worker": "celery-worker.log",
    "postgres": "postgres.log",
    "postgresql": "postgres.log",
}


@tool
def tail_log(log_name: str, n_lines: int = 20) -> str:
    """
    Read the last N lines of a classroom log file under data/logs/.

    MUST use this tool whenever the user asks to show, tail, or read logs.
    Never invent host paths like /var/log/... — only these files exist here:
      - nginx-error.log
      - celery-worker.log
      - postgres.log

    Args:
        log_name: Filename under data/logs/, or a short alias.
            Examples: "nginx" → nginx-error.log; "celery" → celery-worker.log;
            "postgres" → postgres.log; or pass the full filename.
        n_lines: How many trailing lines to return (default 20, max 100).
    """
    raw = (log_name or "").strip().replace("\\", "/").split("/")[-1]
    if not raw:
        return "Provide a log file name, e.g. nginx-error.log"

    # Map aliases / bare service names → real filename
    key = raw.lower().removesuffix(".log")
    name = _LOG_ALIASES.get(key, raw)
    if not name.endswith(".log"):
        name = _LOG_ALIASES.get(name.lower(), name)

    # Safe join: stay inside data/logs/ (no path escape)
    path = (LOGS_DIR / name).resolve()
    try:
        path.relative_to(LOGS_DIR.resolve())
    except ValueError:
        return "Refused: path must stay under data/logs/."

    if not path.is_file():
        available = sorted(p.name for p in LOGS_DIR.glob("*") if p.is_file())
        return f"Log not found: {name}. Available: {', '.join(available)}"

    lines = path.read_text(encoding="utf-8", errors="replace").splitlines()
    n = max(1, min(int(n_lines), 100))
    tail = lines[-n:]
    return f"--- {name} (last {len(tail)} lines) ---\n" + "\n".join(tail)


TOOLS = [check_service_status, search_runbooks, tail_log]

CHAT_SYSTEM_PROMPT = """You are a DevOps on-call helper for a classroom lab (not a real host).

Tools:
1) check_service_status — check if a service is up/down FIRST when asked about health.
2) search_runbooks — RAG search over real files in data/ (via Chroma). Use for fix steps.
3) tail_log — read recent lines from data/logs/. Available files ONLY:
   - nginx-error.log  (alias: nginx)
   - celery-worker.log  (alias: celery / celery-worker)
   - postgres.log  (alias: postgres)

Rules:
- Use tools instead of guessing status, runbook steps, or log contents.
- ANY request to show / tail / read / view logs MUST call tail_log with a filename
  under data/logs/ (or an alias above). Example: "show me logs of nginx" →
  tail_log(log_name="nginx-error.log") or log_name="nginx".
- NEVER invent host paths like /var/log/nginx/... — those do not exist in this lab.
  Quote only what tail_log returns.
- You may call more than one tool.
- Keep final answers short (2–4 sentences) unless asked for detail.
- Cite runbook sources when you used search_runbooks.
- Remember earlier turns in this conversation (same thread_id).
"""

_CHECKPOINTER = InMemorySaver()


def build_chat_agent(checkpointer=None):
    """Free-text on-call agent with tools + short-term memory."""
    # Fail early with a clear message if student forgot ingest
    get_vectorstore()
    return create_agent(
        model=get_llm(),
        tools=TOOLS,
        system_prompt=CHAT_SYSTEM_PROMPT,
        checkpointer=checkpointer or _CHECKPOINTER,
    )


def fill_incident_ticket(user_text: str, assistant_reply: str) -> IncidentTicket:
    """
    Second pass: structured fill ONLY (no tools).
    Groq cannot combine tool calling with response_format / JSON mode.
    """
    structured = get_llm().with_structured_output(IncidentTicket)
    prompt = (
        "Fill an IncidentTicket from this on-call exchange. "
        "Use only facts from the assistant reply (do not invent status/runbook).\n"
        "Severity: stopped production-ish service => high/critical; "
        "warning => medium; info-only => low. "
        "Set needs_human_approval=True for high/critical or prod-impacting actions.\n\n"
        f"User request:\n{user_text}\n\n"
        f"Assistant reply (may include tool results):\n{assistant_reply}\n"
    )
    return structured.invoke(prompt)


def ask_chat(agent, thread_id: str, question: str) -> str:
    """Invoke chat agent; return free-text answer."""
    config = {"configurable": {"thread_id": thread_id}}
    result = agent.invoke(
        {"messages": [{"role": "user", "content": question}]},
        config,
    )
    return result["messages"][-1].content


def ask_ticket(chat_agent, thread_id: str, question: str) -> Optional[IncidentTicket]:
    """
    Ticket mode = two LLM calls (Groq-safe):
      1) chat agent with tools + memory
      2) structured-only fill → IncidentTicket
    """
    reply = ask_chat(chat_agent, thread_id, question)
    return fill_incident_ticket(question, reply)
