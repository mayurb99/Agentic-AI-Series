# demo_2_conditional_routing.py
# Lecture 9 -- Demo 2: Conditional edges (fully offline)
#
# Client story: Expense / reimbursement approval
#   An employee submits a claim. After intake we BRANCH:
#
#                        +--> auto_approve   --> END
#   START -> intake -> validate
#                        +--> manager_review --> END
#
#   Policy: amount <= 500  → auto_approve
#           amount >  500  → manager_review  (human gate)
#
# The router is just an if/else that returns the NEXT NODE NAME.
#
# Run:  python demos/demo_2_conditional_routing.py
# Needs: nothing (no API key)

import operator
import sys
from typing import Annotated, TypedDict

from langgraph.graph import END, START, StateGraph

sys.stdout.reconfigure(encoding="utf-8", errors="replace")


# =============================================================================
# STATE  (clipboard — expense claim form)
# =============================================================================

class ExpenseState(TypedDict):
    claim_id: str
    employee: str
    amount: float
    description: str
    status: str
    notes: Annotated[list[str], operator.add]  # append notes
    decision: str


# =============================================================================
# NODES
# =============================================================================

def intake(state: ExpenseState) -> dict:
    """Accept the claim into the reimbursement queue."""
    return {
        "status": "received",
        "notes": [f"intake: claim {state['claim_id']} from {state['employee']}"],
    }


def validate(state: ExpenseState) -> dict:
    """Basic validation — confirm amount is present and positive."""
    amount = state["amount"]
    if amount <= 0:
        return {
            "status": "invalid",
            "notes": ["validate: amount must be > 0"],
        }
    return {
        "status": "validated",
        "notes": [f"validate: amount = {amount:.2f} OK"],
    }


def auto_approve(state: ExpenseState) -> dict:
    """Under-limit path — system approves without a manager."""
    return {
        "decision": "auto_approved",
        "status": "approved",
        "notes": [
            f"auto_approve: {state['claim_id']} approved "
            f"(amount {state['amount']:.2f} <= 500)"
        ],
    }


def manager_review(state: ExpenseState) -> dict:
    """Over-limit path — pause for manager (we only mark the handoff here)."""
    return {
        "decision": "pending_manager",
        "status": "awaiting_manager",
        "notes": [
            f"manager_review: {state['claim_id']} needs manager "
            f"(amount {state['amount']:.2f} > 500)"
        ],
    }


# =============================================================================
# ROUTER  (special: returns a NODE NAME, not a state update)
# =============================================================================

def route_by_amount(state: ExpenseState) -> str:
    """Read amount and pick the next step. Returns a STRING node name."""
    if state["amount"] <= 500:
        return "auto_approve"
    return "manager_review"


# =============================================================================
# BUILD GRAPH
# =============================================================================

def build_graph():
    builder = StateGraph(ExpenseState)

    builder.add_node("intake", intake)
    builder.add_node("validate", validate)
    builder.add_node("auto_approve", auto_approve)
    builder.add_node("manager_review", manager_review)

    builder.add_edge(START, "intake")
    builder.add_edge("intake", "validate")

    # Conditional edge = "after validate, call the router"
    builder.add_conditional_edges(
    "validate",
    route_by_amount,
    {
        "auto_approve": "auto_approve",
        "manager_review": "manager_review",
    },
)
    builder.add_edge("auto_approve", END)
    builder.add_edge("manager_review", END)

    return builder.compile()


# =============================================================================
# HELPER: run one claim and print the result
# =============================================================================

def run_case(
    graph,
    claim_id: str,
    employee: str,
    amount: float,
    description: str,
) -> None:
    print("\n" + "-" * 70)
    print(f"CASE: {claim_id} / {employee} / amount={amount:.2f}")
    print("-" * 70)

    result = graph.invoke(
        {
            "claim_id": claim_id,
            "employee": employee,
            "amount": amount,
            "description": description,
            "status": "new",
            "notes": [],
            "decision": "",
        }
    )

    print(f"  status   = {result['status']}")
    print(f"  decision = {result['decision']}")
    print("  notes:")
    for note in result["notes"]:
        print(f"    - {note}")


# =============================================================================
# MAIN
# =============================================================================

def main() -> None:
    print()
    print("LECTURE 9 -- DEMO 2: Conditional routing")
    print("=" * 70)
    print(
        "\n"
        "  Client story: Expense / reimbursement approval\n"
        "\n"
        "  ASCII map:\n"
        "                         +--> auto_approve   --> END\n"
        "    START -> intake -> validate\n"
        "                         +--> manager_review --> END\n"
        "\n"
        "  Policy: amount <= 500 → auto_approve; else → manager_review\n"
        "  Router returns the NEXT NODE NAME (a string), not a state dict.\n"
    )

    graph = build_graph()
    png_data = graph.get_graph().draw_mermaid_png()

    with open("graph_2.png", "wb") as f:
        f.write(png_data)

    # Under limit → auto_approve
    run_case(
        graph,
        claim_id="EXP-3001",
        employee="Alex Chen",
        amount=85.50,
        description="Client lunch receipt",
    )
    # Over limit → manager_review
    run_case(
        graph,
        claim_id="EXP-3002",
        employee="Sam Rivera",
        amount=1250.00,
        description="Conference travel + hotel",
    )

    print("\n" + "=" * 70)
    print("TAKEAWAYS")
    print("=" * 70)
    print(
        "\n"
        "  1. Fixed edge       = always go to B\n"
        "  2. Conditional edge = router(state) returns the next node name\n"
        "  3. Same pattern for leave > 5 days or production-access requests\n"
        "  4. Graphs shine when business rules need named paths + human gates\n"
    )


if __name__ == "__main__":
    main()
