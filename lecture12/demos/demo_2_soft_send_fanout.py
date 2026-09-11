# demo_2_soft_send_fanout.py
# Lecture 12 -- Demo 2: Soft intro to Send() fan-out (NOT deep map-reduce)
#
# We dispatch the SAME summarize job to N docs in parallel with Send().
# Keep it tiny — deep map-reduce / long-doc patterns come in later lectures.
#
# Run: python demos/demo_2_soft_send_fanout.py
# Needs: GROQ_API_KEY in demos/.env


#                    ┌──→ summarize doc 1 ──┐
#                    │                      │
#START → fan_out ────┼──→ summarize doc 2 ──┼──→ rollup → END
#                    │                      │
#                    └──→ summarize doc 3 ──┘
from __future__ import annotations

import operator
import sys
from typing import Annotated, TypedDict

from langchain_core.messages import HumanMessage, SystemMessage
from langgraph.graph import END, START, StateGraph
from langgraph.types import Send

from _client import get_llm

sys.stdout.reconfigure(encoding="utf-8", errors="replace")


DOCS = [
    "payments: p95 latency 820ms after 1.9.0; error rate 1.1%",
    "auth: OK; cert rotated yesterday; no spike",
    "checkout: queue depth 40 (warn threshold 30)",
]


class FanState(TypedDict):
    docs: list[str]
    summaries: Annotated[list[str], operator.add]
    rollup: str


class DocState(TypedDict):
    """State for ONE fan-out worker."""
    doc: str
    summaries: Annotated[list[str], operator.add]


def fan_out(state: FanState) -> list[Send]:
    """Return one Send per doc — soft map step."""
    return [Send("summarize_one", {"doc": d, "summaries": []}) for d in state["docs"]]


def summarize_one(state: DocState) -> dict:
    llm = get_llm()
    msg = llm.invoke(
        [
            SystemMessage(content="Summarize in <=12 words. No fluff."),
            HumanMessage(content=state["doc"]),
        ]
    )
    text = msg.content if hasattr(msg, "content") else str(msg)
    return {"summaries": [text.strip()]}


def rollup(state: FanState) -> dict:
    llm = get_llm()
    joined = "\n".join(f"- {s}" for s in state["summaries"])
    msg = llm.invoke(
        [
            SystemMessage(content="One Slack sentence combining these bullets."),
            HumanMessage(content=joined),
        ]
    )
    text = msg.content if hasattr(msg, "content") else str(msg)
    return {"rollup": text.strip()}


def build_graph():
    b = StateGraph(FanState)
    b.add_node("summarize_one", summarize_one)
    b.add_node("rollup", rollup)
    # START fans out via Send list; all workers land in summaries; then rollup
    b.add_conditional_edges(START, fan_out, ["summarize_one"])
    b.add_edge("summarize_one", "rollup")
    b.add_edge("rollup", END)
    return b.compile()


def main() -> None:
    print()
    print("LECTURE 12 -- DEMO 2: Soft Send() fan-out")
    print("=" * 70)
    print(
        "\nAnalogy: dispatch the same job to N workers (map), then one rollup.\n"
        "We keep it light — NOT a full map-reduce chapter.\n"
        "\nASCII:\n"
        "  START --Send(doc1)--> summarize_one \\\n"
        "       --Send(doc2)--> summarize_one  +--> rollup --> END\n"
        "       --Send(doc3)--> summarize_one /\n"
    )

    try:
        graph = build_graph()
    except RuntimeError as exc:
        print(f"\nERROR: {exc}")
        sys.exit(1)

    result = graph.invoke({"docs": DOCS, "summaries": [], "rollup": ""})
    print("Per-doc summaries:")
    for s in result["summaries"]:
        print(f"  - {s}")
    print("\nRollup:\n ", result["rollup"])

    print("\n" + "=" * 70)
    print("TAKEAWAYS")
    print("=" * 70)
    print(
        "1. Send(node, state_piece) = fan-out one job to many workers.\n"
        "2. Annotated list + operator.add gathers worker results.\n"
        "3. Deep map-reduce / long-doc patterns wait for later lectures.\n"
        "4. Next lecture (L13): LangSmith — see latency & tool loops in traces.\n"
    )


if __name__ == "__main__":
    main()
