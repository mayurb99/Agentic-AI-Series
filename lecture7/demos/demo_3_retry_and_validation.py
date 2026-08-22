# demo_3_retry_and_validation.py
# Lecture 7 -- Demo 3: Validators + retry when validation fails
#
# Types alone are not enough. A field named "increase" should never
# be negative. We enforce that with @field_validator.
#
# PART A  Manual retry around with_structured_output (LangChain)
# PART B  instructor max_retries= (automatic, raw Groq SDK)
# PART C  LangChain .with_retry() (automatic — may NOT feed error into prompt)
#
# Run: python demos/demo_3_retry_and_validation.py

import logging
import sys
from typing import Literal

import instructor
from groq import Groq
from pydantic import BaseModel, ValidationError, field_validator

from langchain_groq import ChatGroq

from _client import GROQ_API_KEY, MODEL

sys.stdout.reconfigure(encoding="utf-8", errors="replace")

for name in ("groq", "httpx", "httpcore", "urllib3"):
    logging.getLogger(name).setLevel(logging.WARNING)


class IncidentImpact(BaseModel):
    """Impact report with one business rule types cannot express alone."""

    ticket_id: str
    severity: Literal["low", "medium", "high", "critical"]
    error_rate_increase_percent: int
    summary: str

    @field_validator("error_rate_increase_percent")
    @classmethod
    def must_be_non_negative(cls, v: int) -> int:
        if v < 0:
            raise ValueError(
                "error_rate_increase_percent must be >= 0. "
                "If the rate went DOWN, report 0 -- never a negative 'increase'."
            )
        return v


TEXT = (
    "Error rates actually dropped by 12 percent after the last deploy, "
    "everything looks healthy. Ticket INC-4471, severity low."
)


def part_a_manual_retry(max_attempts: int = 3):
    print("\n" + "=" * 70)
    print("PART A -- Manual retry (LangChain)")
    print("=" * 70)
    print("(You catch ValidationError and can feed the error back into the prompt.)\n")

    llm = ChatGroq(model=MODEL, api_key=GROQ_API_KEY, temperature=0, max_tokens=400)
    structured = llm.with_structured_output(IncidentImpact)

    prompt = TEXT
    for attempt in range(1, max_attempts + 1):
        print(f"  Attempt {attempt}...")
        try:
            result = structured.invoke(prompt)
            print(f"  PASSED: {result}")
            return result
        except ValidationError as exc:
            print(f"  FAILED: {str(exc).splitlines()[0]} ...")
            prompt = (
                f"{TEXT}\n\n"
                f"Your previous answer failed validation:\n{exc}\n"
                f"Please correct it and try again."
            )

    print(f"  Gave up after {max_attempts} attempts.")
    return None


def part_b_auto_retry(max_retries: int = 3):
    print("\n" + "=" * 70)
    print("PART B -- Automatic retry (instructor max_retries=)")
    print("=" * 70)
    print("(Debug logging ON so you can see retries.)\n")

    handler = logging.StreamHandler(stream=sys.stdout)
    handler.setFormatter(logging.Formatter("  [%(name)s] %(message)s"))
    logging.basicConfig(level=logging.DEBUG, handlers=[handler], force=True)
    logging.getLogger("instructor.v2.retry").setLevel(logging.DEBUG)

    client = instructor.from_groq(Groq(api_key=GROQ_API_KEY), mode=instructor.Mode.JSON)

    result = client.chat.completions.create(
        model=MODEL,
        response_model=IncidentImpact,
        max_retries=max_retries,
        temperature=0,
        messages=[
            {"role": "system", "content": "Extract a structured incident impact report."},
            {"role": "user", "content": TEXT},
        ],
    )

    logging.getLogger("instructor.v2.retry").setLevel(logging.WARNING)
    logging.disable(logging.CRITICAL)

    print(f"\n  Final result: {result}")
    return result


def part_c_langchain_auto_retry(max_attempts: int = 3):
    print("\n" + "=" * 70)
    print("PART C -- LangChain auto retry (.with_retry())")
    print("=" * 70)
    print("API: structured.with_retry(retry_if_exception_type=..., stop_after_attempt=N)")
    print("Note: unlike Part A, this may just re-invoke -- it does not feed")
    print("the ValidationError text back into the prompt for you.\n")

    llm = ChatGroq(model=MODEL, api_key=GROQ_API_KEY, temperature=0, max_tokens=400)
    structured = llm.with_structured_output(IncidentImpact)

    structured_auto = structured.with_retry(
        retry_if_exception_type=(ValidationError,),
        stop_after_attempt=max_attempts,
        wait_exponential_jitter=False,
    )

    try:
        result = structured_auto.invoke(TEXT)
        print(f"  PASSED: {result}")
        return result
    except ValidationError as exc:
        print(f"  Gave up after {max_attempts} attempts.")
        print(f"  Last error: {str(exc).splitlines()[0]} ...")
        print("  (Expected sometimes: same prompt re-run, no error text fed back.)")
        return None


def main() -> None:
    if not GROQ_API_KEY:
        print("ERROR: GROQ_API_KEY not found.")
        print("Copy demos/.env.example to demos/.env and set GROQ_API_KEY=...")
        sys.exit(1)

    print("\nLECTURE 7 -- DEMO 3: Retry & Validation")
    print("=" * 70)
    print("Business rule: error_rate_increase_percent must be >= 0.")
    print("Source text describes a DECREASE -- attempt 1 often fails.")
    print(f"\nSource: {TEXT}")

    part_a_manual_retry()
    part_b_auto_retry()
    part_c_langchain_auto_retry()

    print("\n" + "=" * 70)
    print("Comparison (manual vs auto is NOT LangChain-vs-raw):")
    print("  Part A | LangChain + manual loop          | you can feed errors into prompt")
    print("  Part B | instructor + max_retries (auto)  | raw API / no LangChain")
    print("  Part C | LangChain + .with_retry() (auto) | may just re-invoke, no error text")
    print("-" * 70)
    print("Takeaways:")
    print("  - @field_validator enforces rules types cannot express.")
    print("  - Manual OR auto retry both work on LangChain or raw stacks.")
    print("  - Passing validation = shape OK, not 'every fact is true'.")
    print("=" * 70)


if __name__ == "__main__":
    main()
