# demo_3_longterm_entity_memory.py
# Lecture 6 -- Demo 3: Long-term facts across NEW conversations (simple)
#
# Demo 1+2 memory is scoped to ONE thread_id.
# Start a new thread (new day / new ticket) and that short-term memory is gone.
#
# Long-term memory uses a Store + tools that read/write it:
#
#   store = InMemoryStore()
#   create_agent(..., checkpointer=..., store=store)
#
# Tools get a hidden `runtime: ToolRuntime` argument (not shown to the LLM)
# so they can call runtime.store.put / .get.
#
# DevOps analogy: short-term = this ticket's chat log;
#                 long-term  = a sticky note on the user/service profile.
#
# Run: python demos/demo_3_longterm_entity_memory.py
# Needs: GROQ_API_KEY in demos/.env

import sys

from langchain.agents import create_agent
from langchain.tools import ToolRuntime
from langchain_core.tools import tool
from langgraph.checkpoint.memory import InMemorySaver
from langgraph.store.memory import InMemoryStore

from _client import get_agent_llm
from _verbose import run_verbose

sys.stdout.reconfigure(encoding="utf-8", errors="replace")

# One fixed demo "user" so every tool call hits the same record.
USER_NAMESPACE = ("users",)
USER_KEY = "demo_ops"


@tool
def remember_about_user(fact: str, runtime: ToolRuntime) -> str:
    """
    Save a fact about the user for future conversations (not just this one).

    Use when the user shares name, role, preferred service, or a preference
    like "keep answers short". These facts survive a brand-new thread_id.

    Args:
        fact: Short fact in third person, e.g. "The user's name is Sam".
    """
    existing = runtime.store.get(USER_NAMESPACE, USER_KEY)
    facts = list(existing.value["facts"]) if existing else []
    facts.append(fact)
    runtime.store.put(USER_NAMESPACE, USER_KEY, {"facts": facts})
    return f"Saved to long-term memory: {fact}"


@tool
def recall_about_user(runtime: ToolRuntime) -> str:
    """
    Look up everything remembered about the user from past conversations,
    even ones with a different thread_id.

    Call this at the start of a new conversation before answering.
    """
    existing = runtime.store.get(USER_NAMESPACE, USER_KEY)
    if not existing or not existing.value.get("facts"):
        return "No saved facts about this user yet."
    facts = existing.value["facts"]
    return "Known facts about the user:\n" + "\n".join(f"- {f}" for f in facts)


def build_agent():
    """
    Both memory systems together (best practice):
      checkpointer -> this conversation's turns
      store        -> facts that outlive the thread
    """
    return create_agent(
        model=get_agent_llm(),
        tools=[remember_about_user, recall_about_user],
        system_prompt="""
You are a helpful DevOps assistant with long-term memory about the user.

Tool rules:
1. remember_about_user — call once per distinct fact (name, role, preference).
2. recall_about_user — call at the START of a conversation before answering.

Keep answers to 1-3 short sentences.
""",
        checkpointer=InMemorySaver(),
        store=InMemoryStore(),
    )


def main() -> None:
    print()
    print("LECTURE 6 -- DEMO 3: Long-term (entity) memory with Store")
    print("=" * 70)
    print(
        "\nFacts about a user survive brand-new thread_ids —\n"
        "something checkpointer-only memory cannot do.\n"
    )

    try:
        agent = build_agent()
    except RuntimeError as exc:
        print(f"\nERROR: {exc}")
        sys.exit(1)

    print("\n" + "=" * 70)
    print("DAY 1 -- thread_id='day-1' -- user introduces themselves")
    print("=" * 70)
    run_verbose(
        agent,
        "Hi! I'm Sam, a platform engineer. I prefer short, direct answers. "
        "I own the payments service.",
        {"configurable": {"thread_id": "day-1"}},
    )

    print("\n" + "=" * 70)
    print("DAY 2 -- NEW thread_id='day-2' -- checkpointer is empty here")
    print("=" * 70)
    print("(if only short-term memory existed, the agent would know nothing)")
    run_verbose(
        agent,
        "What do you know about me so far?",
        {"configurable": {"thread_id": "day-2"}},
    )

    print("\n" + "=" * 70)
    print("DAY 3 -- another new thread -- preference still applied")
    print("=" * 70)
    run_verbose(
        agent,
        "In one sentence: what should I check first if payments is slow?",
        {"configurable": {"thread_id": "day-3"}},
    )

    print("\n" + "=" * 70)
    print("RECAP")
    print("=" * 70)
    print(
        "\n"
        "  checkpointer = remembers THIS conversation (thread_id)\n"
        "  store        = remembers THIS user across conversations\n"
        "\n"
        "  InMemoryStore is RAM-only for this classroom demo.\n"
        "  Production apps use a durable store later — same idea.\n"
    )


if __name__ == "__main__":
    main()
