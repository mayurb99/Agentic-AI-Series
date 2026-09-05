# demo_1_interrupt_before.py
# Lecture 11 -- Demo 1: interrupt_before (expense approval gate)
#
# Client story: expense claim
#   draft_claim --> [GATE] --> submit_to_finance --> done
#
# We compile with interrupt_before=["submit_to_finance"] so the graph
# PAUSES after drafting. Nothing goes to finance until we resume.
#
# Bridge from L10:
#   L10's ReAct loop runs until it finishes (no human pause).
#   Today: first learn the gate alone (no tools yet). Demo 2 adds tools.
#
# Run:  python demos/demo_1_interrupt_before.py
# Needs: nothing (fully offline — no API key)

from __future__ import annotations

import sys
from typing import TypedDict

from langgraph.checkpoint.memory import InMemorySaver
from langgraph.graph import END, START, StateGraph

sys.stdout.reconfigure(encoding="utf-8", errors="replace")


# =============================================================================
# STEP 1: State = the expense claim form (shared clipboard)
# =============================================================================

class ExpenseState(TypedDict):
    employee: str
    amount_usd: float
    category: str
    draft: str
    submitted: bool
    log: str


# =============================================================================
# STEP 2: Nodes = plain functions (no tools, no LLM)
# =============================================================================

def draft_claim(state: ExpenseState) -> dict:
    """Build a short claim summary a manager can review."""
    draft = (
        f"Expense claim for {state['employee']}: "
        f"${state['amount_usd']:.2f} ({state['category']})"
    )
    return {
        "draft": draft,
        "log": "drafted — waiting for human approval before finance",
    }


def submit_to_finance(state: ExpenseState) -> dict:
    """Dangerous step — sends money request to finance.

    In a real system this would call an API / write to a ledger.
    We gate BEFORE this node so a human can stop a bad claim.
    """
    return {
        "submitted": True,
        "log": f"SUBMITTED TO FINANCE: {state['draft']}",
    }


def done_node(state: ExpenseState) -> dict:
    """Final status line after submit (or we never get here if rejected offline)."""
    status = "submitted" if state["submitted"] else "not submitted"
    return {"log": f"done — claim {status}"}


# =============================================================================
# STEP 3: Build the graph + HITL gate
#   START -> draft_claim -> submit_to_finance -> done -> END
#   interrupt_before=["submit_to_finance"]  << the gate
# =============================================================================

def build_graph():
    builder = StateGraph(ExpenseState)
    builder.add_node("draft_claim", draft_claim)
    builder.add_node("submit_to_finance", submit_to_finance)
    builder.add_node("done", done_node)

    builder.add_edge(START, "draft_claim")
    builder.add_edge("draft_claim", "submit_to_finance")
    builder.add_edge("submit_to_finance", "done")
    builder.add_edge("done", END)

    # HITL always needs a checkpointer — a pause must land somewhere.
    # InMemorySaver = classroom RAM (dies when the process exits).
    return builder.compile(
        checkpointer=InMemorySaver(),
        interrupt_before=["submit_to_finance"],
    )


# =============================================================================
# STEP 4: Run — pause, inspect, resume same thread_id
# =============================================================================

def main() -> None:
    print()
    print("LECTURE 11 -- DEMO 1: interrupt_before (expense gate)")
    print("=" * 70)
    print(
        "\nClient story: draft an expense claim, pause BEFORE submit_to_finance.\n"
        "Same idea as a manager Approve button — nothing hits finance until resume.\n"
        "\nBridge from L10: the ReAct loop had no human gate. Today we add one.\n"
    )

    graph = build_graph()

    # thread_id = which "ticket / claim conversation" this pause belongs to
    config = {"configurable": {"thread_id": "expense-claim-101"}}
    start = {
        "employee": "Alex Chen",
        "amount_usd": 750.0,
        "category": "client travel",
        "draft": "",
        "submitted": False,
        "log": "",
    }

    print("\n1) First invoke — runs until the gate...")
    graph.invoke(start, config)
    snap = graph.get_state(config)
    print(f"   next node(s): {snap.next}")
    print(f"   draft: {snap.values.get('draft')}")
    print(f"   submitted? {snap.values.get('submitted')}")
    print("   >>> PAUSED before submit_to_finance (human must approve)")

    print("\n2) Human reviews the draft...")
    print(f"   Draft on screen: {snap.values.get('draft')}")
    print("   Decision: APPROVE — resume same thread_id")

    print("\n3) Second invoke with None — continues from checkpoint...")
    # None input = "keep going from where we paused" (same thread_id)
    graph.invoke(None, config)
    snap2 = graph.get_state(config)
    print(f"   next node(s): {snap2.next}")
    print(f"   submitted? {snap2.values.get('submitted')}")
    print(f"   log: {snap2.values.get('log')}")

    print("\n" + "=" * 70)
    print("TAKEAWAYS")
    print("=" * 70)
    print(
        "1. interrupt_before=['submit_to_finance'] + checkpointer = pause gate.\n"
        "2. Same thread_id resumes from the saved checkpoint.\n"
        "3. invoke(None, config) continues after the human says yes.\n"
        "4. Demo 2: same gate idea ON TOP of an L10 tool loop (MessagesState).\n"
    )


if __name__ == "__main__":
    main()
