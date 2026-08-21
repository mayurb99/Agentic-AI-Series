# _client.py
# One place to build the Groq chat model used by the demos.
#
# Memory demos use create_agent (same as Lecture 5 Demos 2–3),
# so we use the larger agent model for reliable multi-turn behavior.

import os
from pathlib import Path

from dotenv import load_dotenv
from langchain_groq import ChatGroq

# Load demos/.env whether you run from lecture6/ or from demos/
load_dotenv(Path(__file__).resolve().parent / ".env")
load_dotenv()

GROQ_API_KEY = os.getenv("GROQ_API_KEY")

AGENT_MODEL = "openai/gpt-oss-120b"


def _require_api_key() -> None:
    if not GROQ_API_KEY:
        raise RuntimeError(
            "GROQ_API_KEY not found.\n"
            "Copy demos/.env.example to demos/.env and fill in your key\n"
            "from https://console.groq.com/keys"
        )


def get_agent_llm(temperature: float = 0) -> ChatGroq:
    """Larger model for create_agent (multi-turn memory demos)."""
    _require_api_key()
    return ChatGroq(
        model=AGENT_MODEL,
        api_key=GROQ_API_KEY,
        temperature=temperature,
        max_tokens=256,
    )
