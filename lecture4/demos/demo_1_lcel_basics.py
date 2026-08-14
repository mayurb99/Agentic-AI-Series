# demo_1_lcel_basics.py
# Lecture 4 -- Demo 1: LCEL basics -- the pipe operator
#
# THE BIG IDEA
# -------------
# Lecture 3 called Groq by hand every time: build a messages list,
# call the SDK, unpack .choices[0].message.content.
#
# LCEL gives every piece the same interface (Runnable), so you can
# compose them with `|` like a Unix shell pipe:
#   prompt | llm | parser
#
# DEVOPS ANALOGY -- Unix shell pipes
# ----------------------------------
# grep "ERROR" app.log | awk '{print $1}' | sort
# is the same idea as prompt | llm | parser.

import sys

from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate

from _client import get_llm

sys.stdout.reconfigure(encoding="utf-8", errors="replace")


def print_header(title: str) -> None:
    print("\n" + "=" * 70)
    print(title)
    print("=" * 70)


def part_1_the_manual_way() -> None:
    print_header("PART 1: What Lecture 3 made you do by hand")
    print(
        """
  Every demo looked like this:

      response = client.chat.completions.create(
          model=...,
          messages=[{\"role\": \"user\", \"content\": prompt}],
      )
      return response.choices[0].message.content

  That works. LCEL just stops you from rewriting it forever.
"""
    )


def part_2_the_lcel_way(llm) -> None:
    print_header("PART 2: The same call as prompt | llm | parser")

    prompt = ChatPromptTemplate.from_template(
        "Answer in exactly one sentence: {question}"
    )
    parser = StrOutputParser()
    chain = prompt | llm | parser

    print(
        "\n  prompt = ChatPromptTemplate.from_template(...)\n"
        "  parser = StrOutputParser()\n"
        "  chain  = prompt | llm | parser\n"
    )

    question = "What is a load balancer, in DevOps terms?"
    answer = chain.invoke({"question": question})

    print(f"  > {question}")
    print(f"  < {answer}")
    print("\n  One .invoke(). Plain string out. No SDK unpacking.")


def part_3_runnable_interface(llm) -> None:
    print_header("PART 3: Every piece has .invoke() -- same interface")

    prompt = ChatPromptTemplate.from_template("Answer in one sentence: {question}")

    for name, runnable in [("prompt", prompt), ("llm", llm), ("chain", prompt | llm)]:
        print(f"  {name:8s} has .invoke()? {hasattr(runnable, 'invoke')}")

    print("\n  Shared interface = why `|` works on any of them.")


def main() -> None:
    print()
    print("LECTURE 4 -- DEMO 1")
    print("LCEL Basics: The Pipe Operator")
    print("=" * 70)

    try:
        llm = get_llm()
    except RuntimeError as exc:
        print(f"\nERROR: {exc}")
        sys.exit(1)

    part_1_the_manual_way()
    part_2_the_lcel_way(llm)
    part_3_runnable_interface(llm)

    print_header("RECAP")
    print(
        "\n- Lecture 3: manual messages + SDK + unpack\n"
        "- Today: prompt | llm | parser, then chain.invoke(...)\n"
        "- Next: .batch() and .stream() on the same chain"
    )


if __name__ == "__main__":
    main()
