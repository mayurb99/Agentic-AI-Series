# demo_1_custom_tools.py
# Lecture 5 -- Demo 1: Build your first custom tools
#
# Same teaching arc as MLOps L6 Demo 1, but NO RAG / knowledge base.
# Three custom tools, each a different pattern:
#   Tool 1: get_current_datetime()   -- no parameters
#   Tool 2: calculate_days_between() -- two parameters, calculation
#   Tool 3: check_service_status()   -- wraps a simple in-memory dict
#
# Key lesson: the @tool decorator + docstring is ALL you need.
# Then we bind_tools() and show a one-shot "LLM chooses, we run" loop.
#
# Run: python demos/demo_1_custom_tools.py
# Needs: GROQ_API_KEY in demos/.env

import sys
from datetime import date, datetime

from langchain_core.messages import HumanMessage, SystemMessage
from langchain_core.tools import tool

from _client import get_llm

sys.stdout.reconfigure(encoding="utf-8", errors="replace")


# Fake service data -- in real life this would call Kubernetes / systemd.
SERVICES = {
    "nginx": "running",
    "redis": "stopped",
    "postgres": "running",
}


# =============================================================================
# TOOL 1: No parameters -- simplest possible tool
# =============================================================================
@tool
def get_current_datetime() -> str:
    """
    Get the current date and time.
    Use this tool when the user asks about the current date, time, or day of the week.
    Returns a formatted string with the current datetime.
    """
    now = datetime.now()
    return f"Current datetime: {now.strftime('%A, %B %d, %Y at %H:%M:%S')}"


# =============================================================================
# TOOL 2: Two parameters -- calculation tool
# =============================================================================
@tool
def calculate_days_between(date1: str, date2: str) -> str:
    """
    Calculate the number of days between two dates.
    Use this tool when the user asks how many days are between two dates,
    or how long until a future date, or how long ago a past date was.
    Dates must be in YYYY-MM-DD format (e.g. 2024-01-15).

    Args:
        date1: First date in YYYY-MM-DD format
        date2: Second date in YYYY-MM-DD format
    """
    try:
        d1 = date.fromisoformat(date1)
        d2 = date.fromisoformat(date2)
        diff = abs((d2 - d1).days)
        return f"There are {diff} days between {date1} and {date2}."
    except ValueError as e:
        return f"Error parsing dates: {e}. Use YYYY-MM-DD format."


# =============================================================================
# TOOL 3: Wrap a simple dict as a tool (NO vector store / RAG)
# =============================================================================
@tool
def check_service_status(service_name: str) -> str:
    """
    Check whether a service is currently running.
    Use this whenever the user asks if a service is up, down, or healthy.
    Supported services: nginx, redis, postgres.

    Args:
        service_name: Name of the service to check
    """
    name = service_name.lower().strip()
    if name not in SERVICES:
        return f"Unknown service '{name}'. Try: nginx, redis, postgres."
    return f"Service '{name}' is {SERVICES[name].upper()}."


ALL_TOOLS = [get_current_datetime, calculate_days_between, check_service_status]


# =============================================================================
# SHOW: What the LLM actually sees for each tool
# =============================================================================
def show_tool_schemas() -> None:
    """Print name, description, and parameters -- what LangChain sends the LLM."""
    print("\nSTEP 1: What the LLM sees -- tool schemas")
    print("-" * 60)

    for t in ALL_TOOLS:
        print(f"\n  Tool: {t.name}")
        print(f"  Description: {t.description.strip().splitlines()[0]}")
        if t.args:
            print(f"  Parameters: {list(t.args.keys())}")
        else:
            print("  Parameters: none")

    print("\n  Key insight: the LLM reads 'description' to decide IF to call a tool.")
    print("  Write descriptions as if explaining to a colleague.")


# =============================================================================
# DEMO: LLM choosing tools (bind_tools + one-shot manual loop)
# =============================================================================
SYSTEM_PROMPT = """You have access to three tools.

Rules:
- ALWAYS use get_current_datetime for current date/time questions.
- ALWAYS use calculate_days_between for date difference questions.
- ALWAYS use check_service_status when asked if a service is up/down/healthy.
- Answer directly only when no tool is needed (for example, simple math or greetings).
"""

QUESTIONS = [
    "What day of the week is it today?",
    "How many days are there between 2024-01-01 and 2024-12-31?",
    "Is redis currently running?",
    "What is 2 + 2?",  # answerable without any tool
]


def demo_tool_calling(llm) -> None:
    """
    Bind tools to the LLM and show it choosing tools for different questions.
    We use .bind_tools() here -- the raw mechanism.
    Demo 2 wraps this same idea inside create_agent.
    """
    print("\nSTEP 2: LLM choosing which tool to call (bind_tools)")
    print("-" * 60)

    llm_with_tools = llm.bind_tools(ALL_TOOLS)
    tool_by_name = {t.name: t for t in ALL_TOOLS}

    for i, question in enumerate(QUESTIONS, start=1):
        print(f"\n  Question {i}: {question}")
        response = llm_with_tools.invoke(
            [SystemMessage(content=SYSTEM_PROMPT), HumanMessage(content=question)]
        )

        if not response.tool_calls:
            preview = (response.content or "")[:100]
            print(f"  -> No tool called. Direct answer: {preview}")
            continue

        for call in response.tool_calls:
            print(f"  -> Tool chosen: {call['name']}")
            print(f"  -> Arguments:   {call['args']}")
            result = tool_by_name[call["name"]].invoke(call["args"])
            print(f"  -> Tool result: {str(result)[:120]}")


# =============================================================================
# MAIN
# =============================================================================
def main() -> None:
    print()
    print("LECTURE 5 -- DEMO 1: Custom tools with @tool decorator")
    print("=" * 60)

    try:
        llm = get_llm()
    except RuntimeError as exc:
        print(f"\nERROR: {exc}")
        sys.exit(1)

    show_tool_schemas()
    demo_tool_calling(llm)

    print("\n" + "=" * 60)
    print("RECAP")
    print("=" * 60)
    print(
        "\n"
        "  1. @tool + docstring = everything LangChain needs\n"
        "  2. Description is what the LLM reads to decide IF to call\n"
        "  3. Type hints = parameter schema\n"
        "  4. bind_tools() = LLM decides; YOU still run the tool once\n"
        "  5. Next: create_agent runs that loop for you (Demo 2)\n"
    )


if __name__ == "__main__":
    main()
