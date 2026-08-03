# demo_2_prompt_engineering.py
# Lecture 1 -- Demo 2: Zero-shot vs. few-shot vs. chain-of-thought
#
# One real DevOps task, solved three different ways, so the technique
# itself is the analogy -- not just narrated over it:
#
#   Task: classify a raw log line's severity as INFO / WARNING / ERROR /
#   CRITICAL, with a one-line reason.
#
#   Zero-shot   = writing a one-off script with no reference and hoping
#                 it works. We just ask -- no examples, no format hint.
#
#   Few-shot    = copying a working Terraform module example and adapting
#                 it. We show the model 3 already-solved log lines before
#                 asking about the real ones, so it copies both the
#                 severity judgement AND the output format.
#
#   Chain-of-thought = a written incident-response runbook that forces
#                 step-by-step reasoning ("check signals -> weigh severity
#                 -> conclude") instead of jumping straight to a guess.
#
# Watch how accuracy AND output format both improve as the technique
# improves -- especially on the 2nd log line, which is deliberately
# ambiguous (a repeated OOMKill is far more serious than a single one).

import sys

from _client import DEFAULT_MODEL, get_client

# Deliberately tricky: severity here depends on REPETITION/FREQUENCY, not
# just the presence of a scary-sounding word. A model that doesn't reason
# step by step tends to under- or over-rate this one.
LOG_LINES = [
    "Disk usage at 92% on /var/log partition",
    "OOMKilled: container 'payment-api' exceeded memory limit 512Mi, "
    "restarted 4 times in the last 10 minutes",
    "Retrying request to downstream service 'inventory-svc' (attempt 2/5)",
]


def ask(client, prompt: str, max_tokens: int = 200) -> str:
    response = client.chat.completions.create(
        model=DEFAULT_MODEL,
        messages=[{"role": "user", "content": prompt}],
        temperature=0,
        max_tokens=max_tokens,
    )
    return response.choices[0].message.content.strip()


# =========================================================================
# TECHNIQUE 1 -- Zero-shot
# =========================================================================

def zero_shot(client, log_line: str) -> str:
    prompt = (
        "Classify this log line's severity as one of: INFO, WARNING, "
        "ERROR, CRITICAL.\n\n"
        f"Log line: {log_line}"
    )
    return ask(client, prompt)


# =========================================================================
# TECHNIQUE 2 -- Few-shot
# =========================================================================

FEW_SHOT_EXAMPLES = """\
Example 1
Log line: CPU usage at 45% on node-3
SEVERITY: INFO | REASON: Normal operating range, no action needed.

Example 2
Log line: SSL certificate for api.example.com expires in 3 days
SEVERITY: WARNING | REASON: Not broken yet, but will cause an outage soon if ignored.

Example 3
Log line: Database primary unreachable, all writes failing for 5 minutes
SEVERITY: CRITICAL | REASON: Active outage affecting all write traffic right now.

Example 4
Log line: Pod 'checkout-api' crash-looped 6 times in the last 8 minutes
SEVERITY: CRITICAL | REASON: Repeated crashing in a short window is an escalating failure pattern, not a one-off blip.
"""


def few_shot(client, log_line: str) -> str:
    prompt = (
        "Classify log line severity as INFO, WARNING, ERROR, or CRITICAL, "
        "following the exact format shown in these examples:\n\n"
        f"{FEW_SHOT_EXAMPLES}\n"
        "Now classify this one, same format:\n"
        f"Log line: {log_line}\n"
        "SEVERITY:"
    )
    return ask(client, prompt)


# =========================================================================
# TECHNIQUE 3 -- Chain-of-thought
# =========================================================================

def chain_of_thought(client, log_line: str) -> str:
    prompt = (
        "You are triaging a log line, the same way you'd work through an "
        "incident-response runbook. Think step by step, out loud:\n"
        "Step 1 - What signals are present (error keywords, resource "
        "exhaustion, repetition/frequency)?\n"
        "Step 2 - Is this a one-off event or a repeating/escalating "
        "pattern? Repetition changes severity a lot.\n"
        "Step 3 - Based on steps 1-2, assign a final severity: INFO, "
        "WARNING, ERROR, or CRITICAL.\n\n"
        f"Log line: {log_line}\n\n"
        "Keep each step to 1-2 short sentences so the whole answer is "
        "brief. Walk through steps 1-3, then end your answer with "
        "exactly one line in this format:\n"
        "SEVERITY: <level> | REASON: <one sentence>"
    )
    return ask(client, prompt, max_tokens=350)


# =========================================================================
# RUN THE DEMO
# =========================================================================

def run_demo(client):
    for i, log_line in enumerate(LOG_LINES, start=1):
        print("\n" + "=" * 70)
        print(f"LOG LINE {i}: {log_line}")
        print("=" * 70)

        print("\n  -- ZERO-SHOT (no examples, no format hint) --")
        print(f"  {zero_shot(client, log_line)}")

        print("\n  -- FEW-SHOT (3 worked examples given first) --")
        print(f"  {few_shot(client, log_line)}")

        print("\n  -- CHAIN-OF-THOUGHT (forced step-by-step reasoning) --")
        print(f"  {chain_of_thought(client, log_line)}")


# =========================================================================
# MAIN
# =========================================================================

def main():
    print()
    print("LECTURE 1 -- DEMO 2")
    print("Prompt Engineering: Zero-shot vs. Few-shot vs. Chain-of-thought")
    print("=" * 70)

    print(
        "\nSame task, same model, same temperature -- only the prompting\n"
        "technique changes. Watch two things as you read the output:\n"
        "  (1) FORMAT: zero-shot returns a free-form paragraph every time.\n"
        "      Few-shot and chain-of-thought reliably return the exact\n"
        "      'SEVERITY: X | REASON: Y' line, because that's the format\n"
        "      they were shown/told to follow -- that consistency is what\n"
        "      you actually need if another system parses this output.\n"
        "  (2) REASONING: log line 2 is the hard one -- a single OOMKill\n"
        "      is a WARNING, but FOUR restarts in 10 minutes is a crash\n"
        "      loop and should be CRITICAL. Chain-of-thought's reasoning\n"
        "      is the only technique that visibly walks through WHY,\n"
        "      step by step -- worth reading even when the final answer\n"
        "      happens to agree with the other techniques.\n"
    )

    try:
        client = get_client()
    except RuntimeError as exc:
        print(f"\nERROR: {exc}")
        sys.exit(1)

    run_demo(client)

    print("\n" + "=" * 70)
    print("What happened internally?\n")
    print("1. Zero-shot: fastest to write, but a free-form paragraph every")
    print("   time -- nothing else in your pipeline can reliably parse that.")
    print("2. Few-shot: showing 4 solved examples anchors both the severity")
    print("   judgement AND the exact output format -- like giving someone")
    print("   a working Terraform module to copy instead of a blank file.")
    print("3. Chain-of-thought: forcing 'signals -> pattern -> conclusion'")
    print("   is the same discipline as a written incident runbook -- it")
    print("   catches nuance zero-shot tends to skip past.")
    print("4. There's no single 'best' technique -- pick based on how much")
    print("   the task needs consistency (few-shot) vs. reasoning depth")
    print("   (chain-of-thought) vs. how cheap/fast it needs to be")
    print("   (zero-shot, fewer tokens = lower bill).")
    print("=" * 70)


if __name__ == "__main__":
    main()
