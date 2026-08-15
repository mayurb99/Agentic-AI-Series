# _client.py
# One place to build the Groq chat model used by the demos.
#
# get_llm()       -- small/fast model (Demo 1 bind_tools one-shot)
# get_agent_llm() -- larger model for create_agent's multi-step loop (Demos 2–3)
#
# Why two models? Small models often keep calling tools forever.
# A bigger model is more reliable at knowing when to stop.

import os
from pathlib import Path

from dotenv import load_dotenv
from langchain_groq import ChatGroq

# Load demos/.env whether you run from lecture5/ or from demos/
load_dotenv(Path(__file__).resolve().parent / ".env")
load_dotenv()

GROQ_API_KEY = os.getenv("GROQ_API_KEY")

DEFAULT_MODEL = "llama-3.1-8b-instant"
AGENT_MODEL = "openai/gpt-oss-120b"


def _require_api_key() -> None:
    if not GROQ_API_KEY:
        raise RuntimeError(
            "GROQ_API_KEY not found.\n"
            "Copy demos/.env.example to demos/.env and fill in your key\n"
            "from https://console.groq.com/keys"
        )


def get_llm(temperature: float = 0) -> ChatGroq:
    """Small model for one-shot bind_tools calls (Demo 1)."""
    _require_api_key()
    return ChatGroq(model=DEFAULT_MODEL, api_key=GROQ_API_KEY, temperature=temperature)


def get_agent_llm(temperature: float = 0) -> ChatGroq:
    """Larger model for create_agent (multi-step tool loop)."""
    _require_api_key()
    return ChatGroq(model=AGENT_MODEL, api_key=GROQ_API_KEY, temperature=temperature)
