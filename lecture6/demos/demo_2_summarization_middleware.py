# demo_2_summarization_middleware.py
# Lecture 6 -- Demo 2: Keep long chats from blowing the context window
#
# Demo 1's checkpointer keeps EVERY message. Long chats grow forever.
# SummarizationMiddleware compresses old turns into one short summary
# once a trigger threshold is hit.
#
#   SummarizationMiddleware(
#       model=llm,
#       trigger=("messages", 6),  # summarize once 6+ messages pile up
#       keep=("messages", 2),     # always keep the 2 most recent in full
#   )
#
# Tiny trigger/keep numbers on purpose so the classroom demo fires fast.
# Real apps use much larger values (or token-based triggers).
#
# Run: python demos/demo_2_summarization_middleware.py
# Needs: GROQ_API_KEY in demos/.env

import sys

from langchain.agents import create_agent
from langchain.agents.middleware import SummarizationMiddleware
from langgraph.checkpoint.memory import InMemorySaver

from _client import get_agent_llm

sys.stdout.reconfigure(encoding="utf-8", errors="replace")


def build_agent():
    llm = get_agent_llm()
    return create_agent(
        model=llm,
        tools=[],
        system_prompt=(
            "You are a helpful deploy-planning assistant. "
            "Answer in 1-2 short sentences."
        ),
        checkpointer=InMemorySaver(),
        middleware=[
            SummarizationMiddleware(
                model=llm,
                trigger=("messages", 6),
                keep=("messages", 2),
            ),
        ],
    )


def describe_state(agent, config) -> None:
    state = agent.get_state(config)
    messages = state.values["messages"]
    print(f"  (state now holds {len(messages)} messages)")

    if messages:
        content = str(getattr(messages[0], "content", ""))
        if content.startswith("Here is a summary of the conversation"):
            print("  >>> SUMMARIZATION FIRED — oldest turns replaced by a summary:")
            print(f"      \"{content[:160]}...\"")


def ask(agent, config, question: str) -> str:
    print(f"\n  > {question}")
    result = agent.invoke(
        {"messages": [{"role": "user", "content": question}]},
        config,
    )
    answer = result["messages"][-1].content
    print(f"  < {answer}")
    describe_state(agent, config)
    return answer


def main() -> None:
    print()
    print("LECTURE 6 -- DEMO 2: SummarizationMiddleware")
    print("=" * 70)
    print(
        "\nSame short-term memory as Demo 1, plus auto-summarize when\n"
        "the message list grows past a tiny classroom threshold.\n"
    )

    try:
        agent = build_agent()
    except RuntimeError as exc:
        print(f"\nERROR: {exc}")
        sys.exit(1)

    config = {"configurable": {"thread_id": "deploy-plan"}}

    print("\n" + "=" * 70)
    print("Simulating a long planning chat (trigger=6, keep=2)")
    print("=" * 70)

    turns = [
        "I'm planning a deploy for service 'payments'.",
        "Target environment is staging first.",
        "We need 3 replicas for the canary.",
        "Rollback plan: previous image tag v1.4.2.",
        "Owner on-call is team Platform.",
        "What service are we deploying, and what's the rollback tag?",
    ]

    for question in turns:
        ask(agent, config, question)

    print("\n" + "=" * 70)
    print("RECAP")
    print("=" * 70)
    print(
        "\n"
        "  1. Checkpointer alone = remember everything (grows forever)\n"
        "  2. SummarizationMiddleware = compress old turns when trigger hits\n"
        "  3. keep= keeps recent messages in full; older ones become a summary\n"
        "  4. Facts from early turns can still survive inside that summary\n"
        "  5. Next (Demo 3): facts that must survive a NEW thread_id\n"
    )


if __name__ == "__main__":
    main()
