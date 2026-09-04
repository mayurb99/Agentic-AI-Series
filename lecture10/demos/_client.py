# _client.py
# One place to build the Groq chat model used by the demos.

import os
from pathlib import Path

from dotenv import load_dotenv
from langchain_groq import ChatGroq

load_dotenv(Path(__file__).resolve().parent / ".env")
load_dotenv()

GROQ_API_KEY = os.getenv("GROQ_API_KEY")
MODEL = "openai/gpt-oss-120b"


def _require_api_key() -> None:
    if not GROQ_API_KEY:
        raise RuntimeError(
            "GROQ_API_KEY not found.\n"
            "Copy demos/.env.example to demos/.env and fill in your key\n"
            "from https://console.groq.com/keys"
        )


def get_llm(temperature: float = 0) -> ChatGroq:
    """ChatGroq for ReAct / tool-calling demos."""
    _require_api_key()
    return ChatGroq(
        model=MODEL,
        api_key=GROQ_API_KEY,
        temperature=temperature,
        max_tokens=512,
    )
