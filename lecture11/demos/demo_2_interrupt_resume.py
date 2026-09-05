# demo_2_interrupt_resume.py
# Lecture 11 -- Demo 2: L10 ReAct loop + HITL gate before submit
#
# Client story: IT + expense helper
#   Employee asks about ticket T-100 and a $750 expense.
#   Agent uses tools (L10 loop), then we pause BEFORE submit_or_close.
#
# ASCII map:
#   START -> agent --(tool_calls?)--> tools -> agent -> ...
#                 --(no tool_calls)--> [GATE] submit_or_close -> END
#
# Bridge from L10:
#   L10 Demo 2 = agent <-> tools until done (then END).
#   L11 Demo 2 = same loop, but "done" goes to a gated submit node.
#
# Bridge from Demo 1:
#   Demo 1 = gate alone (no tools).
#   Demo 2 = gate on a real tool agent (why create_agent alone is not enough).
#
# Run:  python demos/demo_2_interrupt_resume.py
# Needs: GROQ_API_KEY in demos/.env

from __future__ import annotations

import sys

from langchain.tools import tool
from langchain_core.messages import AIMessage, HumanMessage, SystemMessage
from langgraph.checkpoint.memory import InMemorySaver
from langgraph.graph import END, START, MessagesState, StateGraph
from langgraph.prebuilt import ToolNode
from langgraph.types import Command, interrupt

from _client import get_llm

sys.stdout.reconfigure(encoding="utf-8", errors="replace")


# =============================================================================
# STEP 1: Same style tools as L10 (fake IT ticket + expense policy)
# =============================================================================

@tool
def lookup_ticket(ticket_id: str) -> str:
    """Look up an IT service-desk ticket by id like T-100."""
    fake = {
        "t-100": "OPEN — laptop VPN not connecting (priority: high)",
        "t-200": "RESOLVED — password reset completed",
        "t-300": "PENDING — software license waiting on manager",
    }
    return fake.get(ticket_id.strip().lower(), f"UNKNOWN ticket '{ticket_id}'")


@tool
def expense_policy(amount_usd: float) -> str:
    """Return company expense rule for a dollar amount (fake policy)."""
    if amount_usd <= 500:
        return f"${amount_usd:.2f}: AUTO-APPROVE (under $500 threshold)"
    return f"${amount_usd:.2f}: NEEDS MANAGER REVIEW (over $500 threshold)"


TOOLS = [lookup_ticket, expense_policy]
SYSTEM = (
    "You are a concise workplace assistant for IT tickets and expense policy. "
    "Use tools when you need facts. When you have enough facts, give a short "
    "summary for a manager (1-3 sentences). Do not pretend you already submitted."
)


# =============================================================================
# STEP 2: Router after agent — tools OR submit gate (not plain END)
# =============================================================================

def route_after_agent(state: MessagesState) -> str:
    """Like L10 tools_condition, but 'done' goes to submit_or_close."""
    last = state["messages"][-1]
    if getattr(last, "tool_calls", None):
        return "tools"
    return "submit_or_close"


# =============================================================================
# STEP 3: submit_or_close uses interrupt() — pause INSIDE the node
# =============================================================================

def submit_or_close(state: MessagesState) -> dict:
    """Dangerous / side-effect step — close ticket + queue expense for finance.

    interrupt(payload) parks the graph and shows a question to a human.
    Whatever we pass to Command(resume=...) becomes the value of `decision`.
    """
    # Build a short preview from the last AI text (for the human screen)
    last_ai = ""
    for msg in reversed(state["messages"]):
        if isinstance(msg, AIMessage) and not getattr(msg, "tool_calls", None):
            last_ai = str(msg.content)[:200]
            break

    decision = interrupt(
        {
            "question": "Approve submit/close? (approve / reject)",
            "preview": last_ai or "(no AI summary yet)",
            "actions": ["close ticket T-100", "queue $750 expense to finance"],
        }
    )

    if str(decision).lower() in ("approve", "yes", "approved"):
        result = (
            "APPROVED — ticket T-100 marked for close; "
            "$750 expense queued to finance."
        )
    else:
        result = f"REJECTED — no submit. Human said: {decision!r}"

    return {"messages": [AIMessage(content=result)]}


# =============================================================================
# STEP 4: Build L10-style ReAct graph + HITL gate
# =============================================================================

def build_graph():
    llm = get_llm().bind_tools(TOOLS)

    def agent_node(state: MessagesState) -> dict:
        """Reason step — may request tools (same as L10)."""
        messages = [SystemMessage(content=SYSTEM)] + list(state["messages"])
        response = llm.invoke(messages)
        return {"messages": [response]}

    builder = StateGraph(MessagesState)
    builder.add_node("agent", agent_node)
    builder.add_node("tools", ToolNode(TOOLS))
    builder.add_node("submit_or_close", submit_or_close)

    builder.add_edge(START, "agent")
    builder.add_conditional_edges(
        "agent",
        route_after_agent,
        {"tools": "tools", "submit_or_close": "submit_or_close"},
    )
    builder.add_edge("tools", "agent")
    builder.add_edge("submit_or_close", END)

    # Checkpointer required for interrupt() / resume
    return builder.compile(checkpointer=InMemorySaver())


# =============================================================================
# STEP 5: Run — tool loop, pause, approve path + reject path
# =============================================================================

def run_once(label: str, resume_value: str) -> None:
    print("\n" + "-" * 70)
    print(f"SCENARIO: {label} (resume={resume_value!r})")
    print("-" * 70)

    graph = build_graph()
    config = {"configurable": {"thread_id": f"it-expense-{label}"}}

    question = (
        "Look up ticket T-100. Also check expense policy for $750. "
        "Then prepare to submit/close."
    )
    print(f"  User: {question}")

    # First invoke: agent <-> tools, then hits interrupt() inside submit_or_close
    graph.invoke(
        {"messages": [HumanMessage(content=question)]},
        config,
    )
    snap = graph.get_state(config)
    print(f"  next={snap.next}  (waiting on human)")
    if snap.tasks:
        for t in snap.tasks:
            if getattr(t, "interrupts", None):
                print(f"  interrupt payload: {t.interrupts}")

    # Resume with the human decision
    final = graph.invoke(Command(resume=resume_value), config)
    last = final["messages"][-1]
    print(f"  final: {getattr(last, 'content', last)}")


def main() -> None:
    print()
    print("LECTURE 11 -- DEMO 2: L10 tool loop + interrupt() before submit")
    print("=" * 70)
    print(
        "\nClient story: IT ticket + expense — tools first, human gate before submit.\n"
        "\nWhy not only create_agent?\n"
        "  create_agent hides the loop. Approvals need a visible node you can pause.\n"
        "  Hand StateGraph (L10) + interrupt (today) = tool agent with a manager gate.\n"
    )

    try:
        run_once("approve-path", "approve")
        run_once("reject-path", "reject")
    except RuntimeError as exc:
        print(f"\nERROR: {exc}")
        sys.exit(1)

    print("\n" + "=" * 70)
    print("TAKEAWAYS")
    print("=" * 70)
    print(
        "1. L10 loop (MessagesState + tools) still runs — then we gate submit.\n"
        "2. interrupt(payload) pauses INSIDE a node; Command(resume=...) answers.\n"
        "3. Demo 1 used interrupt_before; Demo 2 uses interrupt() after tools.\n"
        "4. create_agent is great for FAQ bots — not enough when you need approvals.\n"
        "5. Demo 3: SqliteSaver so the pause survives a process restart.\n"
    )


if __name__ == "__main__":
    main()
