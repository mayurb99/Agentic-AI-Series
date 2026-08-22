# demo_2_instructor_framework_agnostic.py
# Lecture 7 -- Demo 2: Same idea WITHOUT LangChain
#
# Demo 1 used LangChain's with_structured_output().
# This file uses the `instructor` library + the raw Groq SDK.
# Same result: a validated Pydantic object.
#
# Run: python demos/demo_2_instructor_framework_agnostic.py

import sys
from typing import Literal

import instructor
from groq import Groq
from pydantic import BaseModel, Field

from _client import GROQ_API_KEY, MODEL

sys.stdout.reconfigure(encoding="utf-8", errors="replace")


class IncidentReport(BaseModel):
    """Tiny schema: turn an incident blurb into fields."""

    service: str = Field(description="Affected service name")
    severity: Literal["low", "medium", "high", "critical"] = Field(
        description="How serious it is"
    )
    affected_users_estimate: int = Field(
        description="Rough number of users affected"
    )
    root_cause_guess: str = Field(
        description="One short sentence guessing the cause"
    )


TEXTS = [
    (
        "nginx pods keep getting OOM-killed. Memory hits 95% then crash. "
        "About 2000 customers are seeing 502 errors."
    ),
    (
        "Footer copyright still says 2024 on the marketing site. "
        "Cosmetic only, maybe a few people noticed."
    ),
]


def main() -> None:
    if not GROQ_API_KEY:
        print("ERROR: GROQ_API_KEY not found.")
        print("Copy demos/.env.example to demos/.env and set GROQ_API_KEY=...")
        sys.exit(1)

    print("\nLECTURE 7 -- DEMO 2: instructor (no LangChain)")
    print("=" * 70)
    print("Pattern:")
    print("  1) Wrap the raw Groq client with instructor.from_groq(...)")
    print("  2) Call .create(..., response_model=YourSchema)")
    print("  3) Get a validated Pydantic object back")
    print("=" * 70)

    client = instructor.from_groq(Groq(api_key=GROQ_API_KEY), mode=instructor.Mode.JSON)

    for text in TEXTS:
        print(f"\nRaw text: {text}")

        report = client.chat.completions.create(
            model=MODEL,
            response_model=IncidentReport,
            temperature=0,
            messages=[
                {
                    "role": "system",
                    "content": "Extract a structured incident report.",
                },
                {"role": "user", "content": text},
            ],
        )

        print(f"  type:           {type(report).__name__}")
        print(f"  service:        {report.service}")
        print(f"  severity:       {report.severity}")
        print(f"  affected_users: {report.affected_users_estimate}")
        print(f"  root_cause:     {report.root_cause_guess}")
        print("  Note: severity/user-count are guesses that FIT the schema.")
        print("        Valid shape still does not mean verified truth.")

    print("\n" + "=" * 70)
    print("Takeaways:")
    print("  - Same idea as Demo 1, zero LangChain imports.")
    print("  - Use instructor when your service talks to a raw SDK.")
    print("  - Use with_structured_output when you stay inside LangChain.")
    print("=" * 70)


if __name__ == "__main__":
    main()
