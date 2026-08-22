# demo_1_structured_output_basics.py
# Lecture 7 -- Demo 1: Foundation + with_structured_output
#
# PART 0  JSON string vs dict vs Pydantic  (no API call)
# PART A  Old way: ask for JSON, then parse text
# PART B  New way: llm.with_structured_output(Schema)
# PART C  Tiny L5 link: create_agent + response_format
#
# Run: python demos/demo_1_structured_output_basics.py
# Needs: GROQ_API_KEY in demos/.env  (Part 0 works without it)

import json
import sys
from typing import Literal

from pydantic import BaseModel, Field, ValidationError

from langchain.agents import create_agent
from langchain_core.output_parsers import PydanticOutputParser
from langchain_core.prompts import PromptTemplate

from _client import get_llm

sys.stdout.reconfigure(encoding="utf-8", errors="replace")


class DeploymentRequest(BaseModel):
    """The shape we want: a deployment request as fields, not a paragraph."""

    service_name: str = Field(description="Name of the service to deploy")
    environment: Literal["dev", "staging", "prod"] = Field(
        description="Target environment: must be exactly dev, staging, or prod"
    )
    replicas: int = Field(description="How many copies (replicas) to run")
    requires_approval: bool = Field(
        description="True if a human must approve before deploy (always for prod)"
    )
    reason: str = Field(description="One short sentence: why we are deploying")


REQUEST = (
    "Hey, can you deploy the payment-service to prod with 5 replicas? "
    "This fixes the checkout timeout. Someone should review it first."
)


def part0_foundation() -> None:
    print("\n" + "=" * 70)
    print("PART 0 -- Foundation: JSON string vs dict vs Pydantic")
    print("=" * 70)

    messy = (
        'Sure! Here is the JSON:\n'
        '{"service_name": "payment-service", "environment": "prod", '
        '"replicas": "5", "requires_approval": true, '
        '"reason": "fix checkout timeout"}\n'
        "Let me know if you need anything else!"
    )
    print("\n1) LLM-style free text that CONTAINS JSON:")
    print(f"   type = {type(messy).__name__}")
    print(f"   preview: {messy[:60]}...")
    print("   Problem: you cannot do result.replicas -- it is just text.")

    clean = (
        '{"service_name": "payment-service", "environment": "prod", '
        '"replicas": 5, "requires_approval": true, '
        '"reason": "fix checkout timeout"}'
    )
    as_dict = json.loads(clean)
    print("\n2) After json.loads on CLEAN JSON -- a Python dict:")
    print(f"   type = {type(as_dict).__name__}")
    print(f"   as_dict['replicas'] = {as_dict['replicas']!r}")
    print("   Works, but NOTHING checks that fields/types are correct.")

    print("\n3) Pydantic BaseModel -- check the shape, get a typed object:")
    good = DeploymentRequest.model_validate(as_dict)
    print(f"   OK -> {type(good).__name__}, replicas={good.replicas} (int)")

    bad = {**as_dict, "environment": "production", "replicas": "five"}
    print("\n4) Wrong values -- validation FAILS (good!):")
    print(f"   environment={bad['environment']!r}, replicas={bad['replicas']!r}")
    try:
        DeploymentRequest.model_validate(bad)
    except ValidationError as exc:
        print(f"   ValidationError: {str(exc).splitlines()[0]} ...")

    lie = {
        "service_name": "payment-service",
        "environment": "prod",
        "replicas": 5,
        "requires_approval": True,
        "reason": "the moon is made of cheese",
    }
    obj = DeploymentRequest.model_validate(lie)
    print("\n5) CRITICAL: valid structure != true facts")
    print(f"   Schema-valid reason: {obj.reason!r}")
    print("   Pydantic checked SHAPE and TYPES. It did NOT check truth.")


def part_a_old_parser(llm) -> None:
    print("\n" + "=" * 70)
    print("PART A -- Old way: PydanticOutputParser")
    print("=" * 70)
    print("Ask the model (in English) to format JSON, then parse the text.")

    parser = PydanticOutputParser(pydantic_object=DeploymentRequest)
    instructions = parser.get_format_instructions()
    print("\nFormat instructions (first 180 chars):")
    print(f"  {instructions[:180]}...")

    prompt = PromptTemplate(
        template=(
            "Extract deployment details from the request.\n"
            "{format_instructions}\n\nRequest: {request}\n"
        ),
        input_variables=["request"],
        partial_variables={"format_instructions": instructions},
    )
    chain = prompt | llm | parser

    print(f"\nRequest: {REQUEST}")
    try:
        result = chain.invoke({"request": REQUEST})
        print(f"\nParsed OK: {result}")
    except Exception as exc:
        print(f"\nParsing FAILED: {type(exc).__name__}: {str(exc)[:180]}")
        print("That fragility is why Part B exists.")


def part_b_structured(llm) -> None:
    print("\n" + "=" * 70)
    print("PART B -- New way: llm.with_structured_output(Schema)")
    print("=" * 70)
    print("One line. You get a validated Pydantic object back.")

    structured_llm = llm.with_structured_output(DeploymentRequest)

    print(f"\nRequest: {REQUEST}")
    result = structured_llm.invoke(REQUEST)

    print(f"\nResult type: {type(result).__name__}")
    print(f"  service_name:      {result.service_name}")
    print(f"  environment:       {result.environment}")
    print(f"  replicas:          {result.replicas}")
    print(f"  requires_approval: {result.requires_approval}")
    print(f"  reason:            {result.reason}")
    print("\nNo .parse() call. Attributes work. Shape is enforced.")


def part_c_agent(llm) -> None:
    print("\n" + "=" * 70)
    print("PART C -- L5 link: create_agent + response_format")
    print("=" * 70)
    print("Same create_agent you know from Lectures 5–6.")
    print("response_format= makes the FINAL answer a Pydantic object.")
    print("(tools=[] here -- we only care about the typed final answer)")

    agent = create_agent(
        model=llm,
        tools=[],
        system_prompt="Extract a DeploymentRequest from the user message.",
        response_format=DeploymentRequest,
    )

    result = agent.invoke({"messages": [{"role": "user", "content": REQUEST}]})
    obj = result.get("structured_response")

    print(f"\nresult['structured_response'] type: {type(obj).__name__}")
    if obj is None:
        print("ERROR: structured_response was None")
        return
    print(f"  service_name: {obj.service_name}")
    print(f"  environment:  {obj.environment}")
    print(f"  replicas:     {obj.replicas}")
    print("\nWhen to use what:")
    print("  plain LLM              -> chat / free text (L5 default)")
    print("  with_structured_output -> one call, fill a schema (Part B)")
    print("  create_agent + format  -> agent may use tools, then finish typed")


def main() -> None:
    print("\nLECTURE 7 -- DEMO 1: Foundation + Structured Output")
    print("=" * 70)

    part0_foundation()

    try:
        llm = get_llm()
    except RuntimeError as exc:
        print(f"\nERROR: {exc}")
        sys.exit(1)

    part_a_old_parser(llm)
    part_b_structured(llm)
    part_c_agent(llm)

    print("\n" + "=" * 70)
    print("Takeaways:")
    print("  - JSON string != dict != Pydantic model")
    print("  - Schema checks SHAPE. It does not prove facts are true.")
    print("  - Prefer with_structured_output over text parsers.")
    print("  - create_agent(..., response_format=Schema) -> structured_response")
    print("=" * 70)


if __name__ == "__main__":
    main()
