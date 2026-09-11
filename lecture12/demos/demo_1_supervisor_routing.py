# demo_1_supervisor_routing.py
# Lecture 12 -- Demo 1: Supervisor picks next worker (researcher / writer / FINISH)
#
# Soft multi-agent: ONE graph, supervisor node routes.
# Routing RULES are deterministic (classroom-reliable); LLM only writes a short reason.
#
# Run: python demos/demo_1_supervisor_routing.py
# Needs: GROQ_API_KEY in demos/.env

from __future__ import annotations

import operator
import sys
from typing import Annotated, Literal, TypedDict

from langchain_core.messages import HumanMessage, SystemMessage
from langgraph.graph import END, START, StateGraph

from _client import get_llm

sys.stdout.reconfigure(encoding="utf-8", errors="replace")


class TeamState(TypedDict):
    task: str
    research_notes: str
    draft: str
    next_worker: str
    notes: Annotated[list[str], operator.add]


def choose_next(state: TeamState) -> str:
    """Deterministic commander rules (no flaky tool_choice)."""
    if not (state.get("research_notes") or "").strip():
        return "researcher"
    if not (state.get("draft") or "").strip():
        return "writer"
    return "FINISH"


def supervisor(state: TeamState) -> dict:
    nxt = choose_next(state)
    llm = get_llm()
    reason_msg = llm.invoke(
        "One short sentence: why should an incident commander "
        f"send the ticket to '{nxt}' next? Task: {state['task']}"
    )
    reason = (reason_msg.content if hasattr(reason_msg, "content") else str(reason_msg)).strip()
    return {
        "next_worker": nxt,
        "notes": [f"supervisor -> {nxt} ({reason[:120]})"],
    }


def route_from_state(state: TeamState) -> Literal["researcher", "writer", "__end__"]:
    nxt = state.get("next_worker", "FINISH")
    if nxt == "researcher":
        return "researcher"
    if nxt == "writer":
        return "writer"
    return "__end__"


def researcher(state: TeamState) -> dict:
    llm = get_llm()
    msg = llm.invoke(
        [
            SystemMessage(content="List 3 short bullet facts. No intro."),
            HumanMessage(content=f"Research briefly: {state['task']}"),
        ]
    )
    text = msg.content if hasattr(msg, "content") else str(msg)
    return {
        "research_notes": text.strip(),
        "notes": ["researcher: wrote notes"],
    }


def writer(state: TeamState) -> dict:
    llm = get_llm()
    msg = llm.invoke(
        [
            SystemMessage(content="Write a 2-sentence status update for Slack."),
            HumanMessage(
                content=(
                    f"Task: {state['task']}\n"
                    f"Notes:\n{state['research_notes']}"
                )
            ),
        ]
    )
    text = msg.content if hasattr(msg, "content") else str(msg)
    return {"draft": text.strip(), "notes": ["writer: wrote draft"]}


def build_graph():
    b = StateGraph(TeamState)
    b.add_node("supervisor", supervisor)
    b.add_node("researcher", researcher)
    b.add_node("writer", writer)

    b.add_edge(START, "supervisor")
    b.add_conditional_edges(
        "supervisor",
        route_from_state,
        {"researcher": "researcher", "writer": "writer", "__end__": END},
    )
    b.add_edge("researcher", "supervisor")
    b.add_edge("writer", "supervisor")
    return b.compile()


def main() -> None:
    print()
    print("LECTURE 12 -- DEMO 1: Supervisor routing")
    print("=" * 70)
    print(
        "\nAnalogy: incident commander assigns on-call specialists.\n"
        "  START -> supervisor <-> researcher\n"
        "                      <-> writer\n"
        "                      -> END\n"
        "\nRouting rules are deterministic; LLM only explains the choice.\n"
    )

    try:
        graph = build_graph()
    except RuntimeError as exc:
        print(f"\nERROR: {exc}")
        sys.exit(1)

    result = graph.invoke(
        {
            "task": "payments p95 latency spike after deploy 1.9.0",
            "research_notes": "",
            "draft": "",
            "next_worker": "",
            "notes": [],
        }
    )

    print("\nTrace (notes):")
    for n in result["notes"]:
        print(f"  - {n}")
    print("\nResearch notes:\n", result["research_notes"][:500])
    print("\nDraft:\n", result["draft"][:500])

    print("\n" + "=" * 70)
    print("TAKEAWAYS")
    print("=" * 70)
    print(
        "1. Supervisor = router brain; workers = specialists.\n"
        "2. Workers return to supervisor (not to each other).\n"
        "3. Soft multi-agent: one graph; supervisor routes specialists.\n"
    )


if __name__ == "__main__":
    main()
