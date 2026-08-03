# demo_1_raw_api_basics.py
# Lecture 1 -- Demo 1: Your first raw LLM call, tokens, and temperature
#
# This is the "hello world" of talking to an LLM with nothing but a plain
# SDK -- no framework, no agent, no memory. Three things to notice:
#
#   1. An LLM call is a stateless request/response, exactly like calling a
#      REST endpoint on a microservice. You send messages in, you get one
#      message back, and the server keeps nothing about you afterward.
#
#   2. Every response carries a `usage` object -- prompt_tokens,
#      completion_tokens, total_tokens. This IS your bill. Think of it the
#      same way you think about a cloud invoice: it's itemized by unit of
#      work consumed, not by "one request costs $X flat."
#
#   3. `temperature` controls how much randomness the model injects.
#      temperature=0 is a deterministic, reproducible rollout -- same input,
#      same output, every time. temperature=1 is closer to chaos
#      engineering -- deliberately injecting randomness to explore the
#      space of possible answers.
#
# We'll also deliberately blow past the context window on purpose, so you
# see the real error instead of just hearing about it in a slide.

import sys

from _client import DEFAULT_MODEL, get_client


# =========================================================================
# PART 1 -- Your first raw call
# =========================================================================

def part_1_first_call(client):
    print("\n" + "=" * 70)
    print("PART 1 -- Your first raw API call")
    print("=" * 70)

    print(
        "\nThink of this exactly like calling POST /predict on a stateless\n"
        "microservice: you send a payload (messages), you get a response\n"
        "back, and the server remembers nothing about this call the moment\n"
        "it's done.\n"
    )

    response = client.chat.completions.create(
        model=DEFAULT_MODEL,
        messages=[
            {
                "role": "system",
                "content": "You are a concise assistant. Answer in 1 sentence.",
            },
            {
                "role": "user",
                "content": "What is a REST API, in DevOps terms?",
            },
        ],
        temperature=0,
    )
    print(response)
    answer = response.choices[0].message.content
    usage = response.usage

    print(f"  > What is a REST API, in DevOps terms?")
    print(f"  < {answer}")

    print("\n  -- Response metadata (this is your itemized bill) --")
    print(f"  prompt_tokens     (input,  what you sent)  = {usage.prompt_tokens}")
    print(f"  completion_tokens (output, what came back) = {usage.completion_tokens}")
    print(f"  total_tokens      (input + output)          = {usage.total_tokens}")
    print(
        "\n  Same idea as a cloud bill: you're not charged 'one request',\n"
        "  you're charged per unit of work -- like CPU-seconds or GB\n"
        "  processed. Input tokens and output tokens are billed as\n"
        "  separate line-items, same as ingress vs. compute vs. egress."
    )


# =========================================================================
# PART 2 -- Temperature: the chaos-engineering knob
# =========================================================================

def part_2_temperature(client):
    print("\n" + "=" * 70)
    print("PART 2 -- Temperature: the chaos-engineering knob")
    print("=" * 70)

    prompt = (
        "Suggest one name for a new internal DevOps CLI tool. "
        "Reply with ONLY the name, nothing else -- no explanation."
    )

    print(
        "\ntemperature=0 -> deterministic, reproducible. Like a blue/green\n"
        "  rollout: same input, same output, every single time.\n"
        "temperature=1 -> high randomness. Like a chaos-monkey run: same\n"
        "  input, different output each time, on purpose.\n"
    )

    print(f"  Prompt (same every time): \"{prompt}\"\n")

    print("  -- temperature=0, run 3x --")
    for i in range(3):
        response = client.chat.completions.create(
            model=DEFAULT_MODEL,
            messages=[{"role": "user", "content": prompt}],
            temperature=0,
            max_tokens=15,
        )
        print(f"    run {i + 1}: {response.choices[0].message.content.strip()}")

    print("\n  -- temperature=1, run 3x --")
    for i in range(3):
        response = client.chat.completions.create(
            model=DEFAULT_MODEL,
            messages=[{"role": "user", "content": prompt}],
            temperature=1,
            max_tokens=15,
        )
        print(f"    run {i + 1}: {response.choices[0].message.content.strip()}")

    print(
        "\n  Notice: the temperature=0 runs are identical or near-identical.\n"
        "  The temperature=1 runs vary. Pick temperature=0 for anything you\n"
        "  need to be reproducible (config generation, runbook answers).\n"
        "  Pick something higher only when you WANT variety (brainstorming)."
    )


# =========================================================================
# PART 3 -- Context window: the container memory limit
# =========================================================================

def part_3_context_window(client):
    print("\n" + "=" * 70)
    print("PART 3 -- Context window: the container memory limit")
    print("=" * 70)

    print(
        "\nEvery container you run has a memory ceiling. Exceed it and the\n"
        "kernel OOM-kills the process -- it doesn't 'forget', it just hard\n"
        "stops. An LLM's context window is the same kind of hard ceiling,\n"
        "just measured in tokens instead of bytes of RAM.\n"
        "\n"
        "We're about to deliberately send way more tokens than this model\n"
        "allows, on purpose, so you see the real failure instead of just\n"
        "hearing about it.\n"
    )

    # Roughly 1 token ~= 4 characters for English text. This model's
    # context window is well under a million characters, so this reliably
    # overflows it.
    huge_input = "logs are important. " * 400_000

    print(f"  Sending an input of {len(huge_input):,} characters on purpose...")

    try:
        client.chat.completions.create(
            model=DEFAULT_MODEL,
            messages=[{"role": "user", "content": huge_input}],
            max_tokens=10,
        )
        print("  (Unexpected: that actually went through. Try an even bigger input.)")
    except Exception as exc:
        print(f"\n  Got the expected failure:\n  {type(exc).__name__}: {exc}")
        print(
            "\n  This is exactly like an OOM-kill or a log ring-buffer\n"
            "  overflowing -- it is a hard resource ceiling, not the model\n"
            "  being forgetful. Once you understand this, every 'memory'\n"
            "  feature in later lectures is really just careful engineering\n"
            "  around this one hard limit."
        )


# =========================================================================
# MAIN
# =========================================================================

def main():
    print()
    print("LECTURE 1 -- DEMO 1")
    print("Raw API Basics: tokens, temperature, and the context window")
    print("=" * 70)

    try:
        client = get_client()
    except RuntimeError as exc:
        print(f"\nERROR: {exc}")
        sys.exit(1)

    part_1_first_call(client)
    part_2_temperature(client)
    part_3_context_window(client)

    print("\n" + "=" * 70)
    print("What happened internally?\n")
    print("1. Every call was a fresh, stateless request -- like a REST call")
    print("   to a microservice. Nothing carried over between calls.")
    print("2. usage.total_tokens is your itemized bill for that one call.")
    print("3. temperature controls determinism vs. randomness -- 0 for")
    print("   reproducibility, higher only when you want variety.")
    print("4. The context window is a hard ceiling, measured in tokens,")
    print("   exactly like a container's memory limit.")
    print("=" * 70)


if __name__ == "__main__":
    main()
