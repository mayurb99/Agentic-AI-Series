# demo_1_messages_and_toolnode.py
# Lecture 10 -- Demo 1: MessagesState + bind_tools + ToolNode (one shot)
#
# Client story: HR helpdesk — look up leave balance once
#   PART A  MessagesState = chat transcript as graph state
#   PART B  @tool + llm.bind_tools  (model REQUESTS a tool)
#   PART C  ToolNode RUNS the tool once
#
# Bridge from L9:
#   L9 = you drew nodes and edges (wiring). Tools were paused on purpose.
#   L10 = put tools back into that graph. Demo 1 = pieces only (no loop yet).
#
# Bridge from L5/L8:
#   create_agent hid this loop. Today you see each piece by hand.
#
# Run:  python demos/demo_1_messages_and_toolnode.py
# Needs: GROQ_API_KEY in demos/.env

#              ┌─────────┐
#              │  START  │
#              └────┬────┘
#                   │
#                   ▼
#          ┌────────────────┐
#          │     tools      │
#          │   ToolNode     │
#          └───────┬────────┘
#                  │
#                  ▼
#             ┌─────────┐
#             │   END   │
#             └─────────┘

from __future__ import annotations

import sys

from langchain.tools import tool
from langchain_core.messages import HumanMessage
from langgraph.graph import END, START, MessagesState, StateGraph
from langgraph.prebuilt import ToolNode

from _client import get_llm

sys.stdout.reconfigure(encoding="utf-8", errors="replace")


# =============================================================================
# STEP 1: One simple HR tool (fake lookup — like a payroll API stub)
# =============================================================================

@tool
def get_leave_balance(employee_id: str) -> str:
    """Look up remaining leave days for an employee id like E101."""
    fake = {
        "e101": "14 days remaining (annual leave)",
        "e202": "3 days remaining (annual leave)",
        "e303": "0 days remaining — waitlist for unpaid leave",
    }
    key = employee_id.strip().lower()
    return fake.get(key, f"UNKNOWN employee_id '{employee_id}' — not in HR directory")


TOOLS = [get_leave_balance]


# =============================================================================
# STEP 2: PART A — MessagesState is the shared chat clipboard
# =============================================================================

def part_a_messages_state() -> None:
    print("\n" + "=" * 70)
    print("STEP / PART A -- MessagesState (chat transcript as state)")
    print("=" * 70)
    print(
        "\nL9 used a custom TypedDict (ticket form / expense form).\n"
        "MessagesState is a ready-made TypedDict with a 'messages' list.\n"
        "Analogy: the employee's HR chat thread — every node appends messages.\n"
    )
    state: MessagesState = {
        "messages": [HumanMessage(content="How many leave days do I have?")]
    }
    print(f"  state keys: {list(state.keys())}")
    print(f"  first message type: {type(state['messages'][0]).__name__}")


# =============================================================================
# STEP 3: PART B — bind_tools = model may REQUEST a tool (does not run it)
# =============================================================================

def part_b_bind_tools():
    print("\n" + "=" * 70)
    print("STEP / PART B -- Model REQUESTS a tool (bind_tools)")
    print("=" * 70)
    print(
        "\nbind_tools tells the LLM which tools exist.\n"
        "The model may return tool_calls — that is a REQUEST, not execution.\n"
    )

    llm = get_llm()
    bound = llm.bind_tools(TOOLS)
    msg = bound.invoke(
        [HumanMessage(content="What is the leave balance for employee E101?")]
    )
    print(f"\n  AI content preview: {str(msg.content)[:80]!r}")
    print(f"  tool_calls count: {len(msg.tool_calls)}")
    for tc in msg.tool_calls:
        print(f"    -> {tc['name']}({tc['args']})")
    return msg


# =============================================================================
# STEP 4: PART C — ToolNode = actually RUN the requested tool
# =============================================================================

def part_c_toolnode(ai_msg) -> None:
    print("\n" + "=" * 70)
    print("STEP / PART C -- ToolNode RUNS the requested tool")
    print("=" * 70)
    print(
        "\nAnalogy: HR portal runner — the LLM only asked for leave balance;\n"
        "ToolNode actually calls get_leave_balance(...).\n"
        "\nNote: ToolNode is meant to live inside a compiled graph (Demo 2),\n"
        "so we wrap it in a one-node graph for this one-shot demo.\n"
    )
    # Tiny graph: START -> tools -> END
    builder = StateGraph(MessagesState)
    builder.add_node("tools", ToolNode(TOOLS))
    builder.add_edge(START, "tools")
    builder.add_edge("tools", END)
    tiny = builder.compile()

    out = tiny.invoke({"messages": [ai_msg]})
    for m in out["messages"]:
        if m.type == "tool":
            print(f"  ToolMessage: {m.content}")


# =============================================================================
# MAIN


# =============================================================================

def main() -> None:
    print()
    print("LECTURE 10 -- DEMO 1: MessagesState + ToolNode")
    print("=" * 70)
    print(
        "Client story: HR helpdesk leave lookup (pieces only — loop comes in Demo 2)\n"
        "L9 = graph wiring. Today = put tools into that wiring."
    )
    try:
        get_llm()
    except RuntimeError as exc:
        print(f"\nERROR: {exc}")
        sys.exit(1)

    part_a_messages_state()
    ai_msg = part_b_bind_tools()
    if not ai_msg.tool_calls:
        print("\n  (Model answered without tools — still OK for teaching bind_tools.)")
    else:
        part_c_toolnode(ai_msg)

    print("\n" + "=" * 70)
    print("TAKEAWAYS")
    print("=" * 70)
    print(
        "1. MessagesState holds the conversation (like L9 state, but chat-shaped).\n"
        "2. bind_tools = model may emit tool_calls (REQUEST).\n"
        "3. ToolNode = actually run those calls (ACT).\n"
        "4. Demo 2 wires this into a LOOP with tools_condition.\n"
        "5. create_agent (L5–L8) automated this exact loop — Demo 3 proves it.\n"
    )


if __name__ == "__main__":
    main()
