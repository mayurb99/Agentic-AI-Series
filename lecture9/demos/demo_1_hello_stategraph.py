# demo_1_hello_stategraph.py
# Lecture 9 -- Demo 1: Hello StateGraph (fully offline)
#
# Client story: IT Service Desk ticket intake
#   A SaaS company receives an employee ticket.
#   The workflow is a straight line (no branches yet):
#
#     START --> intake --> classify --> prioritize --> summarize --> END
#
# L8 used create_agent (a ready-made graph).
# Today you draw a tiny graph yourself:
#   State  = shared clipboard (the ticket form)
#   Node   = one step (a Python function)
#   Edge   = arrow to the next step
#
# Run:  python demos/demo_1_hello_stategraph.py
# Needs: nothing (no API key)

import operator
import sys
from typing import Annotated, TypedDict

from langgraph.graph import END, START, StateGraph

sys.stdout.reconfigure(encoding="utf-8", errors="replace")


# =============================================================================
# STEP 1: State = the shared clipboard every node can read/write
# =============================================================================
#
# TypedDict = a plain dict with named keys (like a ticket form).
# notes uses operator.add so each node APPENDS notes instead of replacing them.

class TicketState(TypedDict):
    ticket_id: str
    raw_request: str
    category: str       # "password_reset" | "software_access" | "other"
    priority: str       # "low" | "medium" | "high"
    summary: str
    notes: Annotated[list[str], operator.add]  # append, don't overwrite


# =============================================================================
# STEP 2: Nodes = plain functions
#   Input:  full state
#   Output: a PARTIAL dict of changes (LangGraph merges them in)
# =============================================================================

def intake(state: TicketState) -> dict:
    """Log that the ticket entered the service desk queue."""
    return {
        "notes": [f"intake: accepted {state['ticket_id']}"],
    }


def classify(state: TicketState) -> dict:
    """Classify the request from simple keyword rules (no LLM)."""
    text = state["raw_request"].lower()

    if "password" in text or "reset" in text or "locked out" in text:
        category = "password_reset"
    elif "access" in text or "license" in text or "install" in text:
        category = "software_access"
    else:
        category = "other"

    return {
        "category": category,
        "notes": [f"classify: category = {category}"],
    }


def prioritize(state: TicketState) -> dict:
    """Set priority from category (fake IT policy)."""
    # Password lockouts block work → high
    # Software access needs a manager later → medium
    # Everything else → low
    rules = {
        "password_reset": "high",
        "software_access": "medium",
        "other": "low",
    }
    priority = rules.get(state["category"], "low")

    return {
        "priority": priority,
        "notes": [f"prioritize: priority = {priority}"],
    }


def summarize(state: TicketState) -> dict:
    """Write a one-line ticket summary for the helpdesk queue."""
    summary = (
        f"[{state['priority'].upper()}] {state['category']} — "
        f"{state['raw_request'][:60]}"
    )
    return {
        "summary": summary,
        "notes": ["summarize: queue summary written"],
    }


# =============================================================================
# STEP 3: Build the graph
#   START --> intake --> classify --> prioritize --> summarize --> END
# =============================================================================

def build_graph():
    builder = StateGraph(TicketState)

    # Register the four steps
    builder.add_node("intake", intake)
    builder.add_node("classify", classify)
    builder.add_node("prioritize", prioritize)
    builder.add_node("summarize", summarize)

    # Wire the arrows (always go left -> right — no branching yet)
    builder.add_edge(START, "intake")
    builder.add_edge("intake", "classify")
    builder.add_edge("classify", "prioritize")
    builder.add_edge("prioritize", "summarize")
    builder.add_edge("summarize", END)

    # compile() turns the blueprint into something you can .invoke()
    return builder.compile()


# =============================================================================
# MAIN
# =============================================================================

def main() -> None:
    print()
    print("LECTURE 9 -- DEMO 1: Hello StateGraph")
    print("=" * 70)
    print(
        "\n"
        "  Client story: IT Service Desk ticket intake\n"
        "\n"
        "  ASCII map:\n"
        "    START --> intake --> classify --> prioritize --> summarize --> END\n"
        "\n"
        "  Straight line only — no branches yet (those come in Demo 2).\n"
    )

    # ---- show the starting clipboard ----
    print("=" * 70)
    print("STARTING STATE")
    print("=" * 70)
    start = {
        "ticket_id": "IT-1001",
        "raw_request": "I am locked out — need a password reset for SSO",
        "category": "unknown",
        "priority": "unknown",
        "summary": "",
        "notes": ["opened by employee portal"],
    }
    print(f"  {start}")

    # ---- run the graph ----
    print("\n" + "=" * 70)
    print("RUN  (graph.invoke)")
    print("=" * 70)
    graph = build_graph()
    png_data = graph.get_graph().draw_mermaid_png()

    with open("graph_1.png", "wb") as f:
        f.write(png_data)
    result = graph.invoke(start)

    print(f"  ticket_id = {result['ticket_id']}")
    print(f"  category  = {result['category']}")
    print(f"  priority  = {result['priority']}")
    print(f"  summary   = {result['summary']}")
    print("  notes:")
    for note in result["notes"]:
        print(f"    - {note}")

    # ---- recap ----
    print("\n" + "=" * 70)
    print("TAKEAWAYS")
    print("=" * 70)
    print(
        "\n"
        "  1. State  = TypedDict clipboard every node shares\n"
        "  2. Node   = function(state) -> partial update dict\n"
        "  3. Edges + START/END + compile() = runnable pipeline\n"
        "  4. Next demo: expense claims with an if-branch (auto vs manager)\n"
    )


if __name__ == "__main__":
    main()
