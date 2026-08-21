# demo_1_short_term_memory.py
# Lecture 6 -- Demo 1: Short-term memory (same create_agent as L5 + checkpointer)
#
# Lecture 5's create_agent forgot everything between calls.
# Today we add ONE thing: checkpointer=InMemorySaver()
# Then pass the SAME thread_id on every turn of one conversation.
#
#   create_agent(..., checkpointer=InMemorySaver())
#   agent.invoke(..., {"configurable": {"thread_id": "ticket-42"}})
#
# Same thread_id  -> remembers earlier turns
# Different thread_id -> fresh conversation
# No checkpointer  -> always forgets (quick contrast below)
#
# Run: python demos/demo_1_short_term_memory.py
# Needs: GROQ_API_KEY in demos/.env

import sys

from langchain.agents import create_agent
from langgraph.checkpoint.memory import InMemorySaver

from _client import get_agent_llm

sys.stdout.reconfigure(encoding="utf-8", errors="replace")


def build_agent_with_memory():
    """Same create_agent as Lecture 5 — plus a checkpointer for short-term memory."""
    return create_agent(
        model=get_agent_llm(),
        tools=[],
        system_prompt=(
            "You are a concise DevOps helper. "
            "Answer in 1-2 short sentences."
        ),
        checkpointer=InMemorySaver(),
    )


def build_agent_no_memory():
    """Lecture-5 style: create_agent with NO checkpointer — every call is fresh."""
    return create_agent(
        model=get_agent_llm(),
        tools=[],
        system_prompt=(
            "You are a concise DevOps helper. "
            "Answer in 1-2 short sentences."
        ),
    )


def ask(agent, thread_id: str, question: str) -> str:
    config = {"configurable": {"thread_id": thread_id}}
    print(f"\n  [thread={thread_id}] > {question}")

    result = agent.invoke(
        {"messages": [{"role": "user", "content": question}]},
        config,
    )
    answer = result["messages"][-1].content
    print(f"  [thread={thread_id}] < {answer}")

    state = agent.get_state(config)
    count = len(state.values["messages"])
    print(f"  (checkpointer for '{thread_id}' now holds {count} messages)")
    return answer


def ask_no_memory(agent, question: str) -> str:
    """Invoke with no thread_id — proves Lecture-5-style forgetfulness."""
    print(f"\n  [NO MEMORY] > {question}")
    result = agent.invoke({"messages": [{"role": "user", "content": question}]})
    answer = result["messages"][-1].content
    print(f"  [NO MEMORY] < {answer}")
    return answer


def main() -> None:
    print()
    print("LECTURE 6 -- DEMO 1: Short-term memory (checkpointer + thread_id)")
    print("=" * 70)
    print(
        "\nSame create_agent as Lecture 5.\n"
        "New knob: checkpointer=InMemorySaver() + thread_id on each call.\n"
    )

    try:
        agent = build_agent_with_memory()
        forgetful = build_agent_no_memory()
    except RuntimeError as exc:
        print(f"\nERROR: {exc}")
        sys.exit(1)

    # ------------------------------------------------------------------
    # Contrast: Lecture 5 style (no checkpointer) forgets
    # ------------------------------------------------------------------
    print("\n" + "=" * 70)
    print("CONTRAST — Without memory (Lecture 5 style)")
    print("=" * 70)
    ask_no_memory(forgetful, "My name is Maya. I own the nginx service.")
    ask_no_memory(forgetful, "What is my name, and which service do I own?")
    print("\n  ^ Second call has no saved history — the agent typically cannot recall.")

    # ------------------------------------------------------------------
    # Part 1: same thread remembers
    # ------------------------------------------------------------------
    print("\n" + "=" * 70)
    print("PART 1 — Same thread_id: the agent remembers")
    print("=" * 70)
    ask(agent, "ticket-42", "Hi! My name is Maya and I own the nginx service.")
    ask(agent, "ticket-42", "What is my name, and which service do I own?")
    ask(agent, "ticket-42", "Give me one tip for keeping that service healthy.")

    # ------------------------------------------------------------------
    # Part 2: different thread = blank slate
    # ------------------------------------------------------------------
    print("\n" + "=" * 70)
    print("PART 2 — Different thread_id: no memory of ticket-42")
    print("=" * 70)
    ask(agent, "ticket-99", "What is my name?")

    # ------------------------------------------------------------------
    # Part 3: back to original thread
    # ------------------------------------------------------------------
    print("\n" + "=" * 70)
    print("PART 3 — Back to ticket-42: memory is still there")
    print("=" * 70)
    ask(agent, "ticket-42", "Just to confirm — what's my name again?")

    print("\n" + "=" * 70)
    print("RECAP")
    print("=" * 70)
    print(
        "\n"
        "  1. create_agent alone = forgets (Lecture 5)\n"
        "  2. checkpointer=InMemorySaver() = place to save turns\n"
        "  3. Same thread_id = load those turns back in\n"
        "  4. Different thread_id = fresh conversation\n"
        "  5. InMemorySaver is RAM-only — gone when the script exits\n"
        "  6. Next: long chats fill the context window — Demo 2 summarizes\n"
    )


if __name__ == "__main__":
    main()
