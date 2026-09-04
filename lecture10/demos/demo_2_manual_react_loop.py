# demo_2_manual_react_loop.py
# Lecture 10 -- Demo 2: Full manual ReAct loop (StateGraph)
#
# Client story: IT + expense helper for an employee
#   "Is ticket T-100 open? If expense is $750, does policy need a manager?"
#
#   START -> agent --(tools_condition)--> tools -> agent -> ... -> END
#
# Reason (LLM) -> Act (ToolNode) -> Observe (tool result in messages) -> again
#
# Bridge from L9:
#   L9 Demo 2 used a hand-written router (amount <= 500?).
#   Today tools_condition is the router: tool_calls? -> tools, else END.
#
# Bridge to create_agent:
#   This graph IS what create_agent builds for you. Demo 3 puts them side by side.
#
# Run:  python demos/demo_2_manual_react_loop.py
# Needs: GROQ_API_KEY in demos/.env

#                  ┌─────────┐
#                  │  START  │
#                  └────┬────┘
#                       │
#                       ▼
#                ┌─────────────┐
#                │    agent    │
#                │  LLM node   │
#                └──────┬──────┘
#                       │
#                       ▼
#              ┌──────────────────┐
#              │ tools_condition  │
#              │ "Need a tool?"   │
#              └───────┬──────────┘
#                    YES│       │NO
#                       │       │
#                       ▼       ▼
#                ┌─────────┐  ┌─────┐
#                │  tools  │  │ END │
#                │ToolNode │  └─────┘
#                └────┬────┘
#                     │
#                     │
#                     └──────────────┐
#                                    │
#                                    ▼
#                              ┌─────────────┐
#                              │    agent    │
#                              └─────────────┘
#                                    │
#                                    ▼
#                           tools_condition

from __future__ import annotations

import sys

from langchain.tools import tool
from langchain_core.messages import HumanMessage, SystemMessage
from langgraph.graph import START, MessagesState, StateGraph
from langgraph.prebuilt import ToolNode, tools_condition

from _client import get_llm

sys.stdout.reconfigure(encoding="utf-8", errors="replace")


# =============================================================================
# STEP 1: Two tiny tools (fake IT ticket + fake expense policy)
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
    # Same idea as L9 Demo 2: <= 500 auto, else manager review
    if amount_usd <= 500:
        return f"${amount_usd:.2f}: AUTO-APPROVE (under $500 threshold)"
    return f"${amount_usd:.2f}: NEEDS MANAGER REVIEW (over $500 threshold)"


TOOLS = [lookup_ticket, expense_policy]
SYSTEM = (
    "You are a concise workplace assistant for IT tickets and expense policy. "
    "Use tools when you need facts. Answer in 1-3 short sentences."
)


# =============================================================================
# STEP 2: Build the ReAct graph
#   agent  = Reason (LLM + bind_tools)
#   tools  = Act (ToolNode)
#   tools_condition = if last AI message has tool_calls -> "tools" else END
#   edge tools -> agent = Observe, then Reason again
# =============================================================================

def build_react_graph():
    llm = get_llm().bind_tools(TOOLS)

    def agent_node(state: MessagesState) -> dict:
        """Reason step — may request tools."""
        messages = [SystemMessage(content=SYSTEM)] + list(state["messages"])
        response = llm.invoke(messages)
        return {"messages": [response]}

    builder = StateGraph(MessagesState)
    builder.add_node("agent", agent_node)
    builder.add_node("tools", ToolNode(TOOLS))

    builder.add_edge(START, "agent")
    # Same idea as L9 conditional edges — predicate is tool_calls vs done
    builder.add_conditional_edges("agent", tools_condition)
    builder.add_edge("tools", "agent")  # Observe, then Reason again

    return builder.compile()


# =============================================================================
# STEP 3: Run once with .stream so beginners see each bounce
# =============================================================================

def main() -> None:
    print()
    print("LECTURE 10 -- DEMO 2: Manual ReAct loop")
    print("=" * 70)
    print(
        "\nASCII map (what create_agent hid):\n"
        "  START -> agent --(tool_calls?)--> tools -> agent -> ... -> END\n"
        "                 \\----------------------> END\n"
        "\nL9 analogy: expense amount router.\n"
        "L10 analogy: did the model ask for a tool, or are we done?\n"
    )

    try:
        graph = build_react_graph()
    except RuntimeError as exc:
        print(f"\nERROR: {exc}")
        sys.exit(1)

    question = (
        "Look up ticket T-100. Also tell me the expense policy for a $750 claim."
    )
    print(f"\nUser: {question}\n")
    print("Streaming node updates:\n")

    final_answer = ""
    for update in graph.stream(
        {"messages": [HumanMessage(content=question)]},
        stream_mode="updates",
    ):
        for node, delta in update.items():
            msgs = delta.get("messages", [])
            last = msgs[-1] if msgs else None
            kind = type(last).__name__ if last else "?"
            preview = ""
            if last is not None:
                if getattr(last, "tool_calls", None):
                    preview = f"tool_calls={[tc['name'] for tc in last.tool_calls]}"
                else:
                    preview = str(getattr(last, "content", ""))[:120]
                    if node == "agent" and not getattr(last, "tool_calls", None):
                        final_answer = str(getattr(last, "content", ""))
            print(f"  [{node}] {kind}: {preview}")

    print("\n" + "-" * 70)
    print("FINAL ANSWER:")
    print(final_answer or "(see last [agent] line above)")
    print("-" * 70)

    print("\n" + "=" * 70)
    print("TAKEAWAYS")
    print("=" * 70)
    print(
        "1. agent node = Reason (LLM + bind_tools).\n"
        "2. tools node = Act (ToolNode).\n"
        "3. tools_condition = route on tool_calls vs END (like L9 routers).\n"
        "4. Edge tools->agent = Observe then loop — this IS ReAct.\n"
        "5. create_agent automated this exact graph — see Demo 3.\n"
    )


if __name__ == "__main__":
    main()
