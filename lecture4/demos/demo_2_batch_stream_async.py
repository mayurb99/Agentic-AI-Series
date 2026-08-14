# demo_2_batch_stream_async.py
# Lecture 4 -- Demo 2: invoke, batch, and stream on one chain
#
# THE BIG IDEA
# -------------
# Because a chain is a Runnable, you get these for free:
#   .invoke()  -- one input, wait, one output
#   .batch()   -- many inputs, run together, list of outputs
#   .stream()  -- one input, pieces of output as they arrive
#
# DEVOPS ANALOGY
# --------------
# .invoke()  = one sync REST call
# .batch()   = a small batch job (several calls at once)
# .stream()  = `tail -f` on a live log (see output as it happens)

import sys
import time

from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate

from _client import get_llm

sys.stdout.reconfigure(encoding="utf-8", errors="replace")

QUESTIONS = [
    "What is a container, in one sentence?",
    "What is a load balancer, in one sentence?",
    "What is a reverse proxy, in one sentence?",
]


def print_header(title: str) -> None:
    print("\n" + "=" * 70)
    print(title)
    print("=" * 70)


def build_chain(llm):
    prompt = ChatPromptTemplate.from_template(
        "You are a DevOps tutor. Answer in exactly one sentence: {question}"
    )
    return prompt | llm | StrOutputParser()


def part_1_invoke(chain) -> float:
    print_header("PART 1: .invoke() one question at a time")

    start = time.perf_counter()
    for question in QUESTIONS:
        chain.invoke({"question": question})
    elapsed = time.perf_counter() - start

    print(f"\n3 questions, one .invoke() each: {elapsed:.2f}s total.")
    print("Each call waits for the previous one to finish.")
    return elapsed


def part_2_batch(chain) -> float:
    print_header("PART 2: .batch() -- same 3 questions together")

    start = time.perf_counter()
    answers = chain.batch([{"question": q} for q in QUESTIONS])
    elapsed = time.perf_counter() - start

    for question, answer in zip(QUESTIONS, answers):
        print(f"\n  > {question}")
        print(f"  < {answer}")

    print(f"\n3 questions via .batch(): {elapsed:.2f}s total.")
    print("Usually closer to the slowest call than to the sum of all three.")
    return elapsed


def part_3_stream(chain) -> None:
    print_header("PART 3: .stream() -- tokens as they arrive")

    question = "Explain what a Kubernetes readiness probe does, in 2 sentences."
    print(f"\n  > {question}")
    print("  < ", end="", flush=True)

    start = time.perf_counter()
    first_token_time = None

    for chunk in chain.stream({"question": question}):
        if first_token_time is None:
            first_token_time = time.perf_counter() - start
        print(chunk, end="", flush=True)

    total_time = time.perf_counter() - start
    print(
        f"\n\n  First token: {first_token_time:.3f}s"
        f"  |  Finished: {total_time:.3f}s"
    )
    print("You see the start of the answer before the model is done.")


def main() -> None:
    print()
    print("LECTURE 4 -- DEMO 2")
    print("invoke / batch / stream -- three ways to run one chain")
    print("=" * 70)

    try:
        llm = get_llm()
    except RuntimeError as exc:
        print(f"\nERROR: {exc}")
        sys.exit(1)

    chain = build_chain(llm)

    invoke_time = part_1_invoke(chain)
    batch_time = part_2_batch(chain)
    part_3_stream(chain)

    print_header("RECAP")
    print(
        f"\n- .invoke() loop: {invoke_time:.2f}s for 3 calls (one after another)\n"
        f"- .batch():       {batch_time:.2f}s for the same 3 (together)\n"
        "- .stream(): first token arrives before the last one\n"
        "- Next: LangChain loaders/splitters survey, then full RAG e2e"
    )


if __name__ == "__main__":
    main()
