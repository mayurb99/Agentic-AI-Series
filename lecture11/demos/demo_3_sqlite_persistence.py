# demo_3_sqlite_persistence.py
# Lecture 11 -- Demo 3: SqliteSaver survives "process restart"
#
# Client story: same expense / IT approval thread as Demo 1–2
#   prepare_claim --> wait_for_manager (interrupt) --> submit_or_skip
#
# PART A  Pause mid-flight; write checkpoints.sqlite
# PART B  Fake restart: new graph, SAME file + same thread_id, then resume
#
# Bridge from Demo 1–2:
#   InMemorySaver dies when the process exits.
#   SqliteSaver keeps the paused claim on disk — reopen and continue.
#
# Run:  python demos/demo_3_sqlite_persistence.py
# Needs: langgraph-checkpoint-sqlite (see requirements.txt)
# Offline: no Groq required

from __future__ import annotations

import operator
import sqlite3
import sys
from pathlib import Path
from typing import Annotated, TypedDict

from langgraph.checkpoint.sqlite import SqliteSaver
from langgraph.graph import END, START, StateGraph
from langgraph.types import Command, interrupt

sys.stdout.reconfigure(encoding="utf-8", errors="replace")

DB_PATH = Path(__file__).resolve().parent / "checkpoints.sqlite"


# =============================================================================
# STEP 1: Expense / IT approval form (same themes as L9–L10)
# =============================================================================

class ClaimState(TypedDict):
    thread_label: str
    employee: str
    amount_usd: float
    ticket_id: str
    step: str
    notes: Annotated[list[str], operator.add]
    approved: bool


def prepare_claim(state: ClaimState) -> dict:
    """Draft the claim packet a manager will see."""
    summary = (
        f"{state['employee']}: ${state['amount_usd']:.2f} expense + "
        f"close {state['ticket_id']}"
    )
    return {
        "step": "prepared",
        "notes": [f"prepare: {summary}"],
    }


def wait_for_manager(state: ClaimState) -> dict:
    """Pause INSIDE the node — human must approve or reject."""
    decision = interrupt(
        {
            "question": "Approve expense + ticket close?",
            "employee": state["employee"],
            "amount_usd": state["amount_usd"],
            "ticket_id": state["ticket_id"],
        }
    )
    approved = str(decision).lower() in ("approve", "yes", "approved")
    return {
        "approved": approved,
        "notes": [f"manager: {decision}"],
    }


def submit_or_skip(state: ClaimState) -> dict:
    """Side-effect step — only runs after human resume."""
    if state["approved"]:
        return {
            "step": "submitted",
            "notes": ["submit: expense queued to finance; ticket marked close"],
        }
    return {
        "step": "skipped",
        "notes": ["submit: skipped — manager did not approve"],
    }


# =============================================================================
# STEP 2: Build graph with SqliteSaver (file-backed checkpointer)
# =============================================================================

def build_graph(conn: sqlite3.Connection):
    saver = SqliteSaver(conn)
    b = StateGraph(ClaimState)
    b.add_node("prepare_claim", prepare_claim)
    b.add_node("wait_for_manager", wait_for_manager)
    b.add_node("submit_or_skip", submit_or_skip)
    b.add_edge(START, "prepare_claim")
    b.add_edge("prepare_claim", "wait_for_manager")
    b.add_edge("wait_for_manager", "submit_or_skip")
    b.add_edge("submit_or_skip", END)
    return b.compile(checkpointer=saver)


# =============================================================================
# STEP 3: PART A — pause to disk
# =============================================================================

def part_a_pause_to_disk() -> None:
    print("\n" + "=" * 70)
    print("PART A -- Pause and write checkpoint to Sqlite file")
    print("=" * 70)
    if DB_PATH.exists():
        DB_PATH.unlink()

    conn = sqlite3.connect(str(DB_PATH), check_same_thread=False)
    graph = build_graph(conn)
    # Same story thread as Demo 1/2 — durable now
    config = {"configurable": {"thread_id": "expense-claim-101"}}
    graph.invoke(
        {
            "thread_label": "expense + IT close",
            "employee": "Alex Chen",
            "amount_usd": 750.0,
            "ticket_id": "T-100",
            "step": "start",
            "notes": [],
            "approved": False,
        },
        config,
    )
    snap = graph.get_state(config)
    print(f"  db file: {DB_PATH.name}")
    print(f"  thread_id: expense-claim-101")
    print(f"  next={snap.next}")
    print(f"  notes so far: {snap.values['notes']}")
    print("  >>> Simulating process exit (closing connection)...")
    conn.close()


# =============================================================================
# STEP 4: PART B — "restart" and resume
# =============================================================================

def part_b_restart_and_resume() -> None:
    print("\n" + "=" * 70)
    print("PART B -- New process: reopen Sqlite, resume same thread_id")
    print("=" * 70)
    conn = sqlite3.connect(str(DB_PATH), check_same_thread=False)
    graph = build_graph(conn)
    config = {"configurable": {"thread_id": "expense-claim-101"}}

    snap = graph.get_state(config)
    print(f"  after 'restart', next={snap.next}")
    print(f"  notes recovered: {snap.values['notes']}")
    print("  Resuming with approve...")

    final = graph.invoke(Command(resume="approve"), config)
    print(f"  step={final['step']}")
    print(f"  notes={final['notes']}")
    conn.close()


def main() -> None:
    print()
    print("LECTURE 11 -- DEMO 3: Sqlite persistence across restart")
    print("=" * 70)
    print(
        "\nClient story: expense-claim-101 paused for manager approval.\n"
        "Process 'crashes' while waiting — Sqlite keeps the claim; we resume.\n"
    )
    try:
        part_a_pause_to_disk()
        part_b_restart_and_resume()
    except ImportError as exc:
        print(f"\nERROR: {exc}")
        print("Install: pip install langgraph-checkpoint-sqlite")
        sys.exit(1)

    print("=" * 70)
    print("TAKEAWAYS")
    print("=" * 70)
    print(
        "1. HITL needs a checkpointer — pause must land somewhere.\n"
        "2. Sqlite proves durability: close process, reopen, resume.\n"
        "3. Same thread_id = same claim ticket after restart.\n"
        "4. Next (L12): one durable agent becomes a supervised team.\n"
    )


if __name__ == "__main__":
    main()
