# demo_3_conversational_loop.py
# Lecture 1 -- Demo 3: A conversational loop, built by hand (THE required demo)
#
# This is the curriculum's named hands-on exercise for this lecture. It
# also directly sets up Lecture 7 (Memory & State), so pay close attention
# to what's manual here.
#
# The core idea: an LLM call is stateless (Demo 1). So how does a chatbot
# ever feel like it "remembers" you across a conversation? There is no
# magic -- YOU keep a growing list of every message so far, and you resend
# the ENTIRE list on every single call. The model never "remembers"
# anything between calls; you just keep handing it the whole transcript
# every time, like re-attaching the full email thread every time you reply.
#
# We also hit the context-window problem from Demo 1 head-on: left
# unchecked, this list grows forever. Here we fix it with a deliberately
# crude manual trim (drop the oldest turns once the list gets too long).
# Lecture 7 replaces this exact crude trim with LangChain's
# SummarizationMiddleware -- same problem, smarter fix. Remember this
# demo when you get there.
#
# To try your own conversation: just edit the SCRIPTED_CONVERSATION list
# below and rerun the script. No extra Python syntax needed for that.

import sys

from _client import DEFAULT_MODEL, get_client

SYSTEM_PROMPT = (
    "You are a helpful DevOps AI assistant. Answer in 1-2 short, "
    "practical sentences."
)

# Deliberately tiny, so the manual trim visibly fires during a short,
# scripted demo instead of only after a real hour-long conversation.
MAX_MESSAGES = 7  # counts everything EXCEPT the system message

SCRIPTED_CONVERSATION = [
    "Hi! I'm setting up a new CI/CD pipeline for a service called 'orion-billing'.",
    "What are the main stages I should include?",
    "Should the linting stage run before or after the tests?",
    "What's a sensible timeout for the test stage?",
    "Quick check -- what's the name of the service I mentioned at the start?",
]


def trim_if_needed(messages):
    """
    Manual context-window management: once the conversation grows past
    MAX_MESSAGES, delete the OLDEST user+assistant pair, one pair at a
    time, until it fits again. The system message (index 0) is never
    touched.

    This is deliberately crude -- we just delete old turns, we don't
    summarize them. Lecture 7's SummarizationMiddleware solves this same
    problem by compressing old turns into a summary instead of deleting
    them outright. Same problem, better fix, later.
    """
    system_message = messages[0]
    conversation = messages[1:]

    while len(conversation) > MAX_MESSAGES:
        old_user_msg = conversation.pop(0)
        old_assistant_msg = conversation.pop(0)
        print(
            f"\n  [context-window management] dropped an old message pair "
            f"to stay under the {MAX_MESSAGES}-message cap -- like an old "
            f"log line falling off the front of a fixed-size ring buffer:"
        )
        print(f"    dropped user>      {old_user_msg['content'][:60]}")
        print(f"    dropped assistant> {old_assistant_msg['content'][:60]}")

    return [system_message] + conversation


def send(client, messages):
    response = client.chat.completions.create(
        model=DEFAULT_MODEL,
        messages=messages,
        temperature=0,
        max_tokens=150,
    )
    return response.choices[0].message.content.strip()


# =========================================================================
# THE LOOP
# =========================================================================

def run_loop(client, user_turns):
    # This one list IS the entire "memory" mechanism for this whole demo.
    messages = [{"role": "system", "content": SYSTEM_PROMPT}]

    for user_text in user_turns:
        print(f"\nYou> {user_text}")

        # 1. Append the new user message to the growing list.
        messages.append({"role": "user", "content": user_text})

        # 2. Resend the WHOLE list -- every message so far, every time.
        answer = send(client, messages)

        # 3. Append the assistant's reply too, so it's part of history for
        #    the NEXT call.
        messages.append({"role": "assistant", "content": answer})

        print(f"Assistant> {answer}")
        print(
            f"  (messages list now holds {len(messages)} messages, "
            f"including the system prompt)"
        )

        # 4. Manually keep the list from growing forever.
        messages = trim_if_needed(messages)


# =========================================================================
# MAIN
# =========================================================================

def main():
    print()
    print("LECTURE 1 -- DEMO 3")
    print("A Conversational Loop, Built By Hand")
    print("=" * 70)

    print(
        "\nThere is no memory feature being called here -- just a Python\n"
        "list we grow ourselves and resend, in full, on every single call.\n"
        f"Watch the message count climb, and watch what happens once it\n"
        f"crosses {MAX_MESSAGES} non-system messages.\n"
    )

    try:
        client = get_client()
    except RuntimeError as exc:
        print(f"\nERROR: {exc}")
        sys.exit(1)

    print("Replaying a fixed conversation, one message at a time...")
    print("(Want to try your own? Edit SCRIPTED_CONVERSATION in this file.)")

    run_loop(client, SCRIPTED_CONVERSATION)

    print("\n" + "=" * 70)
    print("What happened internally?\n")
    print("1. Every call was still stateless (Demo 1) -- the model itself")
    print("   remembered nothing between calls.")
    print("2. 'Memory' was entirely our own doing: we kept a Python list")
    print("   and resent the WHOLE thing, every single turn.")
    print("3. Left alone, that list grows forever and eventually blows")
    print("   past the context window (Demo 1, Part 3).")
    print("4. We fixed that here with a crude manual trim -- delete the")
    print("   oldest turns once we cross a cap. It works, but it's lossy:")
    print("   the last question in the scripted run asks about the FIRST")
    print("   thing you said, and by then it may have already been")
    print("   trimmed away, same as an old line falling off a ring buffer.")
    print("5. Lecture 7 replaces this exact home-made trim with LangChain's")
    print("   checkpointer (automatic) and SummarizationMiddleware")
    print("   (compress instead of delete) -- same problem, better fix.")
    print("=" * 70)


if __name__ == "__main__":
    main()
