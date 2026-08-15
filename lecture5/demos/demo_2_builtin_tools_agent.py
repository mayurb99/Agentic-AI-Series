# demo_2_builtin_tools_agent.py
# Lecture 5 -- Demo 2: Built-in tools + create_agent
#
# Same teaching arc as MLOps L6 Demo 2, but NO RAG / knowledge base.
#
# create_agent automatically performs the complete tool-calling loop:
#
#   User Question -> LLM decides -> Tool needed?
#       yes -> run tool -> send tool output back to LLM -> Final Answer
#       no  -> Final Answer directly
#
# Built-ins: Wikipedia + DuckDuckGo (try/except if network flakes).
# Plus one tiny local calculator so the demo still works offline.
#
# Run: python demos/demo_2_builtin_tools_agent.py
# Needs: GROQ_API_KEY in demos/.env

import sys

from langchain.agents import create_agent
from langchain_core.tools import tool

from _client import get_agent_llm
from _verbose import run_verbose

sys.stdout.reconfigure(encoding="utf-8", errors="replace")


# =============================================================================
# Tiny local tool (always available -- no network)
# =============================================================================
@tool
def calculator(expression: str) -> str:
    """
    Evaluate a simple math expression like "15 * 24" or "90 - 72".
    Use this for arithmetic. Do not invent numbers; call this tool.
    """
    allowed = set("0123456789+-*/().% ")
    if not expression or any(ch not in allowed for ch in expression):
        return "Only simple math is allowed (digits and + - * / ( ) . %)."
    try:
        return f"Result: {eval(expression, {'__builtins__': {}}, {})}"
    except Exception as exc:
        return f"Could not evaluate '{expression}': {exc}"


# =============================================================================
# BUILT-IN TOOLS (skip gracefully if import/network fails)
# =============================================================================
def get_builtin_tools() -> list:
    """Load free built-in LangChain tools: Wikipedia + DuckDuckGo."""
    tools = []
    print("\nSTEP 1: Load built-in community tools")
    print("-" * 60)

    try:
        from langchain_community.tools import WikipediaQueryRun
        from langchain_community.utilities import WikipediaAPIWrapper

        _wiki = WikipediaQueryRun(
            api_wrapper=WikipediaAPIWrapper(
                top_k_results=1, doc_content_chars_max=1500
            )
        )

        @tool
        def wikipedia(query: str) -> str:
            """
            Search Wikipedia for encyclopedic information, historical
            events, biographies, inventions, organizations and places.
            """
            try:
                return _wiki.invoke(query)
            except Exception as exc:
                return f"Wikipedia search failed (network/API): {exc}"

        tools.append(wikipedia)
        print("  [OK] Wikipedia loaded")
    except Exception as exc:
        print(f"  [SKIP] Wikipedia unavailable: {exc}")

    try:
        from langchain_community.tools import DuckDuckGoSearchRun

        _ddg = DuckDuckGoSearchRun()

        @tool
        def duckduckgo_search(query: str) -> str:
            """
            Search the internet for current or changing information.
            Use this tool for recent news, latest software versions,
            announcements, and documentation updates.
            """
            try:
                return _ddg.invoke(query)
            except Exception as exc:
                return f"DuckDuckGo search failed (network/API): {exc}"

        tools.append(duckduckgo_search)
        print("  [OK] DuckDuckGo search loaded")
    except Exception as exc:
        print(f"  [SKIP] DuckDuckGo unavailable: {exc}")

    if not tools:
        print("  [WARN] No community tools loaded -- calculator still works.")
    return tools


# =============================================================================
# BUILD THE AGENT
# =============================================================================
AGENT_SYSTEM_PROMPT = """You are a helpful AI assistant. You have access to several tools.

Tool selection rules:

1. Wikipedia
   Use this for historical events, biographies, organizations,
   inventions, and places.

2. DuckDuckGo Search (if available)
   Use this for latest versions, current news, announcements, or
   anything that needs up-to-date information.

3. calculator
   Use this for simple arithmetic only.

Do not invent facts when a tool can answer. If no tool is needed, answer directly.
Give a short final answer.
"""


def build_agent(llm):
    """Build a LangChain agent with built-ins + calculator. No RAG tools."""
    all_tools = get_builtin_tools() + [calculator]

    print("\nSTEP 2: Tools the agent can use")
    print("-" * 60)
    for t in all_tools:
        print(f"  - {t.name}")

    print("\nSTEP 3: Build the agent with create_agent")
    print("-" * 60)
    agent = create_agent(model=llm, tools=all_tools, system_prompt=AGENT_SYSTEM_PROMPT)
    print("  Agent ready.")
    return agent


# =============================================================================
# RUN THE DEMO
# =============================================================================
# Prefer Wikipedia + calculator so class still works if DuckDuckGo flakes.
QUESTIONS = [
    {"q": "Who invented the World Wide Web?", "expect": "Wikipedia"},
    {"q": "What is 15 multiplied by 24?", "expect": "calculator"},
]


def run_agent_demo(agent) -> None:
    """Run example questions to demonstrate automatic tool selection."""
    print("\nSTEP 4: Ask questions (watch the tool loop)")
    print("-" * 60)

    for index, item in enumerate(QUESTIONS, start=1):
        print("\n" + "=" * 60)
        print(f"Question {index}: {item['q']}")
        print(f"Expected Tool: {item['expect']}")
        print("-" * 60)

        try:
            run_verbose(agent, item["q"])
        except Exception as exc:
            print(
                "\n  Agent / network failed (common with live search).\n"
                "  Student-friendly note: the wiring above is still correct.\n"
                f"  Detail: {exc}"
            )

        print("=" * 60)


# =============================================================================
# MAIN
# =============================================================================
def main() -> None:
    print()
    print("LECTURE 5 -- DEMO 2: Built-in Tools + create_agent")
    print("=" * 60)
    print("\ncreate_agent runs the decide -> call -> observe loop for you.")
    print("No RAG / knowledge-base tools in this lecture.")

    try:
        llm = get_agent_llm()
    except RuntimeError as exc:
        print(f"\nERROR: {exc}")
        sys.exit(1)

    agent = build_agent(llm)
    run_agent_demo(agent)

    print("\n" + "=" * 60)
    print("RECAP")
    print("=" * 60)
    print(
        "\n"
        "  1. Built-in tools = reuse published community tools.\n"
        "  2. create_agent runs decide -> call -> observe for you.\n"
        "  3. Network flakes are OK -- try/except keeps the lesson visible.\n"
        "  4. Next: a multi-step DevOps agent with YOUR custom tools (Demo 3).\n"
    )


if __name__ == "__main__":
    main()
