# _client.py
# One place to build an authenticated Groq client from GROQ_API_KEY.
# Same pattern as Lectures 1-2: raw Groq SDK, no LangChain yet.

import os
from pathlib import Path

from dotenv import load_dotenv
from groq import Groq

# Load demos/.env whether you run from lecture3/ or from demos/
load_dotenv(Path(__file__).resolve().parent / ".env")
load_dotenv()  # also allow a .env in the current working directory

GROQ_API_KEY = os.getenv("GROQ_API_KEY")

# Small, fast model -- good for many short lecture calls.
DEFAULT_MODEL = "llama-3.1-8b-instant"


def get_client() -> Groq:
    """Return an authenticated Groq client, or fail with a clear message."""
    if not GROQ_API_KEY:
        raise RuntimeError(
            "GROQ_API_KEY not found.\n"
            "Copy demos/.env.example to demos/.env and fill in your key\n"
            "from https://console.groq.com/keys"
        )
    return Groq(api_key=GROQ_API_KEY)
