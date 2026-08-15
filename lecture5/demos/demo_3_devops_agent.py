# demo_3_devops_agent.py
# Lecture 5 -- Demo 3: DevOps Helper Agent (multi-step tool reasoning)
#
# Same teaching arc as MLOps L6 Demo 3, but tools are local/fake data only.
# NO RAG / Chroma / retrieve_docs tools.
#
# The agent can:
#   1. Check service status
#   2. Look up a runbook entry (plain dict)
#   3. Estimate days until a usage threshold
#
# The interesting part: one tool call influences whether another is needed.
# Example: "is celery-worker down? if so, what do I do?" needs TWO calls.
#
# Run: python demos/demo_3_devops_agent.py
# Needs: GROQ_API_KEY in demos/.env

import sys

from langchain.agents import create_agent
from langchain_core.tools import tool

from _client import get_agent_llm
from _verbose import run_verbose

sys.stdout.reconfigure(encoding="utf-8", errors="replace")


# =============================================================================
# Fake data (in production: real APIs / metrics / a wiki -- still NOT a vector DB)
# =============================================================================
SERVICES = {
    "nginx": {"status": "running", "uptime": "14 days"},
    "redis": {"status": "stopped", "uptime": None},
    "celery-worker": {"status": "stopped", "uptime": None},
}

RUNBOOK = {
    "redis": "Redis is down. Check memory first, then restart redis-server.",
    "celery-worker": (
        "Celery worker stopped. Check broker (Redis/RabbitMQ), then "
        "restart the worker process."
    ),
    "nginx": "Nginx issues: check nginx -t, then reload the config.",
}


# =============================================================================
# TOOL 1: Check service status
# =============================================================================
@tool
def check_service_status(service_name: str) -> str:
    """
    Check whether a service is running.
    Use this when the user asks if a service is up, down, or healthy.
    Supported: nginx, redis, celery-worker.

    Args:
        service_name: Name of the service.
    """
    name = service_name.lower().strip()
    if name not in SERVICES:
        return f"Unknown service '{name}'. Try: nginx, redis, celery-worker."
    info = SERVICES[name]
    if info["status"] == "running":
        return f"Service '{name}' is RUNNING. Uptime: {info['uptime']}."
    return f"Service '{name}' is STOPPED."


# =============================================================================
# TOOL 2: Runbook lookup (plain dict -- NOT a vector store)
# =============================================================================
@tool
def lookup_runbook(service_name: str) -> str:
    """
    Look up runbook guidance for a service incident.
    Use this AFTER checking status, when a service is down or the user
    asks what to do next. Supported: nginx, redis, celery-worker.

    Args:
        service_name: Name of the service.
    """
    name = service_name.lower().strip()
    if name not in RUNBOOK:
        return f"No runbook entry for '{name}'."
    return f"Runbook for {name}: {RUNBOOK[name]}"


# =============================================================================
# TOOL 3: Threshold / days calculator
# =============================================================================
@tool
def days_until_threshold(
    current_percent: float,
    growth_per_day: float,
    threshold_percent: float = 90.0,
) -> str:
    """
    Estimate how many days until usage hits a threshold.
    Use this when the user gives current usage % and growth per day.
    Example: disk at 70% growing 2% per day, when do we hit 90%?

    Args:
        current_percent: Current usage percent.
        growth_per_day: Growth in percent per day.
        threshold_percent: Target threshold (default 90).
    """
    if growth_per_day <= 0:
        return "Growth is zero or negative -- it will not hit the threshold."
    if current_percent >= threshold_percent:
        return f"Already at or above {threshold_percent}%."
    days = (threshold_percent - current_percent) / growth_per_day
    return (
        f"At {current_percent}% now, growing {growth_per_day}%/day, "
        f"you hit {threshold_percent}% in about {days:.1f} days."
    )


TOOLS = [check_service_status, lookup_runbook, days_until_threshold]

AGENT_SYSTEM_PROMPT = """You are a DevOps helper with three tools.

check_service_status
  Use this FIRST when the user asks whether a service is running,
  healthy, available, or down.

lookup_runbook
  Use this AFTER checking status, when a service is stopped or the user
  asks what to do next. Do not invent runbook text.

days_until_threshold
  Use this for usage % / growth-per-day questions.

Use tools instead of guessing. You may call more than one tool.
Give a short final answer when you have enough information.
"""


# Multi-step scenarios (same idea as L6 Demo 3)
SCENARIOS = [
    {
        "title": "Threshold math (one tool)",
        "question": (
            "Disk usage is at 72% and growing 1.5% per day. When do we hit 90%?"
        ),
        "teaching_point": "Single tool call",
    },
    {
        "title": "Status then runbook (two tools)",
        "question": (
            "Check whether celery-worker is running. If it is stopped, "
            "look up the runbook and tell me what to do."
        ),
        "teaching_point": "Status tool followed by runbook tool",
    },
    {
        "title": "Multi-service check",
        "question": (
            "Check nginx and redis. Summarize which services need attention."
        ),
        "teaching_point": "Same tool called more than once",
    },
]


def build_devops_agent(llm):
    """Build the DevOps helper agent. No RAG tools."""
    print("\nSTEP 1: Tools the agent can use")
    print("-" * 60)
    for t in TOOLS:
        print(f"  - {t.name}")

    print("\nSTEP 2: Build the agent with create_agent")
    print("-" * 60)
    agent = create_agent(model=llm, tools=TOOLS, system_prompt=AGENT_SYSTEM_PROMPT)
    print("  Agent ready.")
    return agent


def run_scenarios(agent) -> None:
    """Run every scenario, printing each tool call via run_verbose."""
    print("\nSTEP 3: Multi-step scenarios")
    print("-" * 60)

    for index, scenario in enumerate(SCENARIOS, start=1):
        print("\n" + "=" * 60)
        print(f"Scenario {index}: {scenario['title']}")
        print(f"Teaching Point: {scenario['teaching_point']}")
        print(f"Question: {scenario['question']}")
        print("-" * 60)

        try:
            run_verbose(agent, scenario["question"])
        except Exception as exc:
            print(f"\n  Agent failed: {exc}")

        print("=" * 60)


def main() -> None:
    print()
    print("LECTURE 5 -- DEMO 3: DevOps Helper Agent")
    print("=" * 60)
    print("\nMulti-step tool reasoning. No RAG / vector-store tools.")
    print("Expected pattern for a diagnose question:")
    print("  1. check_service_status()")
    print("  2. If stopped -> lookup_runbook()")
    print("  3. Final answer")

    try:
        llm = get_agent_llm()
    except RuntimeError as exc:
        print(f"\nERROR: {exc}")
        sys.exit(1)

    agent = build_devops_agent(llm)
    run_scenarios(agent)

    print("\n" + "=" * 60)
    print("RECAP")
    print("=" * 60)
    print(
        "\n"
        "  1. create_agent runs: decide -> call -> observe -> decide again.\n"
        "  2. Scenario 2 needed TWO tools; the second depended on the first.\n"
        "  3. We never wrote that loop -- create_agent is the loop.\n"
        "  4. Do not use legacy AgentExecutor; create_agent is the path.\n"
    )


if __name__ == "__main__":
    main()
