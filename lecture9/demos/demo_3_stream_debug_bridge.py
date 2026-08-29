# demo_3_stream_debug_bridge.py
# Lecture 9 -- Demo 3: stream + one LLM node + create_agent bridge
#
# Client story: HR Helpdesk reply drafting
#   PART A  .stream shows each node as it finishes (step debugger)
#   PART B  One node calls ChatGroq to draft a short HR reply
#   PART C  Mental map: create_agent ≈ a pre-built StateGraph
#           (enough for "How many leave days?" FAQ; need a graph for
#            leave > 5 days or production-access approval gates)
#
# Run:  python demos/demo_3_stream_debug_bridge.py
# Needs: GROQ_API_KEY in demos/.env

import operator
import sys
from typing import Annotated, TypedDict

from langgraph.graph import END, START, StateGraph

from _client import get_llm

sys.stdout.reconfigure(encoding="utf-8", errors="replace")


# =============================================================================
# STATE
# =============================================================================

class HrReplyState(TypedDict):
    employee_question: str
    topic: str
    draft_reply: str
    notes: Annotated[list[str], operator.add]


# =============================================================================
# NODES  (tag = classify topic, draft = LLM, stamp = ready marker)
# =============================================================================

def tag_topic(state: HrReplyState) -> dict:
    """Fake step — tag the question as leave / benefits / other (no LLM)."""
    q = state["employee_question"].lower()
    if "leave" in q or "pto" in q or "vacation" in q:
        topic = "leave_policy"
    elif "benefit" in q or "insurance" in q:
        topic = "benefits"
    else:
        topic = "general_hr"
    return {
        "topic": topic,
        "notes": [f"tag_topic: topic = {topic}"],
    }


def draft_reply(state: HrReplyState) -> dict:
    """Call Groq once — write a short, professional HR helpdesk reply."""
    llm = get_llm()
    prompt = (
        "You are an HR helpdesk assistant for an international SaaS company. "
        "Write ONE short, clear reply (2 sentences max) to this employee question. "
        "Be professional and friendly. Do not invent exact leave balances — "
        "point them to the HR portal if needed.\n\n"
        f"Topic tag: {state['topic']}\n"
        f"Question: {state['employee_question']}"
    )
    msg = llm.invoke(prompt)
    text = msg.content if hasattr(msg, "content") else str(msg)
    return {
        "draft_reply": text.strip(),
        "notes": ["draft_reply: LLM wrote HR reply"],
    }


def stamp_ready(state: HrReplyState) -> dict:
    """Mark the draft ready for the agent to send or edit (no LLM)."""
    return {"notes": ["stamp_ready: draft ready for HR agent review"]}


# =============================================================================
# BUILD GRAPH
#   START --> tag_topic --> draft_reply --> stamp_ready --> END
# =============================================================================

def build_graph():
    builder = StateGraph(HrReplyState)
    builder.add_node("tag_topic", tag_topic)
    builder.add_node("draft_reply", draft_reply)
    builder.add_node("stamp_ready", stamp_ready)

    builder.add_edge(START, "tag_topic")
    builder.add_edge("tag_topic", "draft_reply")
    builder.add_edge("draft_reply", "stamp_ready")
    builder.add_edge("stamp_ready", END)

    return builder.compile()


# =============================================================================
# MAIN
# =============================================================================

def main() -> None:
    print()
    print("LECTURE 9 -- DEMO 3: Stream + LLM node + create_agent bridge")
    print("=" * 70)

    # Fail fast with a clear message if .env is missing
    try:
        get_llm()
    except RuntimeError as exc:
        print(f"\nERROR: {exc}")
        sys.exit(1)

    # ------------------------------------------------------------------
    # PART A + B: stream each node update (includes the LLM node)
    # ------------------------------------------------------------------
    print("\n" + "=" * 70)
    print("PART A+B -- .stream updates + one LLM node (HR reply draft)")
    print("=" * 70)
    print(
        "\n"
        "  Client story: HR helpdesk drafts a reply to an employee FAQ.\n"
        "\n"
        "  .stream(..., stream_mode='updates') prints EACH node as it finishes.\n"
        "  Like a ticket tracker: tagged → draft written → ready for review.\n"
        "\n"
        "  ASCII map:\n"
        "    START --> tag_topic --> draft_reply(LLM) --> stamp_ready --> END\n"
    )

    graph = build_graph()
    png_data = graph.get_graph().draw_mermaid_png()

    with open("graph_3.png", "wb") as f:
        f.write(png_data)
    start = {
        "employee_question": "How many annual leave days do I get as a full-time employee?",
        "topic": "",
        "draft_reply": "",
        "notes": [],
    }

    print("Streaming node updates:\n")
    final_reply = ""

    # Each "update" looks like:  {"tag_topic": {"topic": "...", "notes": [...]}}
    for update in graph.stream(start, stream_mode="updates"):
        node_name = list(update.keys())[0]
        delta = update[node_name]

        print(f"  [{node_name}] keys = {list(delta.keys())}")
        if "notes" in delta:
            for note in delta["notes"]:
                print(f"           note: {note}")
        if delta.get("topic"):
            print(f"           topic: {delta['topic']}")
        if delta.get("draft_reply"):
            final_reply = delta["draft_reply"]
            print(f"           draft: {final_reply}")

    print(f"\n  Final draft reply:\n    {final_reply}")

    # ------------------------------------------------------------------
    # PART C: bridge back to create_agent (no API call — just teaching)
    # ------------------------------------------------------------------
    print("\n" + "=" * 70)
    print("PART C -- Bridge: create_agent vs open StateGraph")
    print("=" * 70)
    print(
        """
  You already used create_agent in L5–L8. Mentally:

    from langchain.agents import create_agent   ← LangChain API
    Under the hood LangGraph runs the agent loop (state, steps, memory).

  ENOUGH for create_agent (answer is the product):
    Employee: "How many leave days do I have?"
    → tool lookup (HR system) → clear reply. No manager gate.

  NEED an open StateGraph (flowchart is the product):
    Leave request > 5 days  → pause for manager approve / reject
    OR production-system access request → manager must approve
    Different paths for approve vs reject (named audit hops).

  Today you drew a tiny custom graph (tag → draft → stamp).
  Lecture 10: rebuild the ReAct tool loop BY HAND with ToolNode.

  Rule of thumb:
    - Need a standard tool agent fast?  keep create_agent
    - Need custom gates / branches / HITL? open StateGraph (this phase)
"""
    )

    print("=" * 70)
    print("TAKEAWAYS")
    print("=" * 70)
    print(
        "\n"
        "  1. .stream(updates) = step debugger for graphs\n"
        "  2. An LLM is just another node (call ChatGroq, return a field)\n"
        "  3. create_agent = LangChain API; LangGraph = engine underneath\n"
        "  4. FAQ lookup → create_agent; manager gates → open StateGraph\n"
    )


if __name__ == "__main__":
    main()
