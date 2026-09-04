# demo_3_compare_create_agent.py
# Lecture 10 -- Demo 3: Hand-built ReAct vs create_agent (same tool, same question)
#
# Client story: HR helpdesk leave balance
#   Same question twice:
#     A) Hand-built StateGraph (Demo 2 style) — every wire visible
#     B) create_agent (L5–L8 style) — same loop, managed for you
#
# Point: create_agent automated the graph you just drew in Demo 2.
#
# Remember the L9 story (do not muddy this):
#   create_agent = LangChain API (from langchain.agents import create_agent)
#   LangGraph    = engine under the hood
#   Hand graph   = you own the wires when you need custom gates (L11+)
#
# Run:  python demos/demo_3_compare_create_agent.py
# Needs: GROQ_API_KEY in demos/.env

from __future__ import annotations

import sys

from langchain.agents import create_agent
from langchain.tools import tool
from langchain_core.messages import HumanMessage, SystemMessage
from langgraph.graph import START, MessagesState, StateGraph
from langgraph.prebuilt import ToolNode, tools_condition

from _client import get_llm

sys.stdout.reconfigure(encoding="utf-8", errors="replace")


# =============================================================================
# STEP 1: Same HR tool for both APIs
# =============================================================================

@tool
def get_leave_balance(employee_id: str) -> str:
    """Look up remaining leave days for an employee id like E101."""
    fake = {
        "e101": "14 days remaining (annual leave)",
        "e202": "3 days remaining (annual leave)",
    }
    return fake.get(
        employee_id.strip().lower(),
        f"UNKNOWN employee_id '{employee_id}'",
    )


TOOLS = [get_leave_balance]
QUESTION = "What is the leave balance for employee E101? One short sentence."
SYSTEM = (
    "You are a concise HR helpdesk assistant. "
    "Use tools for facts. Answer in 1-2 short sentences."
)


# =============================================================================
# STEP 2A: Hand-built ReAct (what you learned in Demo 2)
# =============================================================================

def build_manual():
    llm = get_llm().bind_tools(TOOLS)

    def agent_node(state: MessagesState) -> dict:
        msgs = [SystemMessage(content=SYSTEM)] + list(state["messages"])
        return {"messages": [llm.invoke(msgs)]}

    g = StateGraph(MessagesState)
    g.add_node("agent", agent_node)
    g.add_node("tools", ToolNode(TOOLS))
    g.add_edge(START, "agent")
    g.add_conditional_edges("agent", tools_condition)
    g.add_edge("tools", "agent")
    return g.compile()


# =============================================================================
# STEP 2B: create_agent (L5–L8 managed path — LangChain API)
# =============================================================================

def build_create_agent():
    # Import is from langchain.agents — LangChain API.
    # Under the hood it builds a LangGraph loop like Demo 2.
    return create_agent(
        model=get_llm(),
        tools=TOOLS,
        system_prompt=SYSTEM,
    )


# =============================================================================
# STEP 3: Same question, two APIs
# =============================================================================

def main() -> None:
    print()
    print("LECTURE 10 -- DEMO 3: Manual ReAct vs create_agent")
    print("=" * 70)
    print(f"\nSame tool, same question:\n  {QUESTION}\n")
    print(
        "Story check:\n"
        "  create_agent = LangChain API (you import it)\n"
        "  LangGraph    = engine that runs the loop\n"
        "  Hand graph   = you drew that engine yourself in Demo 2\n"
    )

    try:
        manual = build_manual()
        managed = build_create_agent()
    except RuntimeError as exc:
        print(f"\nERROR: {exc}")
        sys.exit(1)

    print("=" * 70)
    print("A) HAND-BUILT StateGraph (Demo 2 style)")
    print("=" * 70)
    r1 = manual.invoke({"messages": [HumanMessage(content=QUESTION)]})
    print(r1["messages"][-1].content)

    print("\n" + "=" * 70)
    print("B) create_agent (L5–L8 style — managed graph)")
    print("=" * 70)
    r2 = managed.invoke({"messages": [{"role": "user", "content": QUESTION}]})
    print(r2["messages"][-1].content)

    print("\n" + "=" * 70)
    print("TAKEAWAYS")
    print("=" * 70)
    print(
        "1. Same job, two APIs: you drew the wires vs create_agent hid them.\n"
        "2. Prefer create_agent for standard tool agents (HR FAQ, leave balance).\n"
        "3. Prefer explicit StateGraph when you need HITL gates (L11),\n"
        "   custom branches (L9 expense router), or multi-agent (L12).\n"
        "4. create_agent is LangChain; LangGraph is the engine — both stay true.\n"
    )


if __name__ == "__main__":
    main()
